import logging
import threading
import weakref
from logging.handlers import RotatingFileHandler

from django.dispatch.dispatcher import Signal
from django.utils.inspect import func_accepts_kwargs
from wagtail.admin.mail import (
    GroupApprovalTaskStateSubmissionEmailNotifier,
    WorkflowStateSubmissionEmailNotifier,
)
from wagtail.models import Task, TaskState, WorkflowState
from wagtail.signals import task_submitted, workflow_submitted

from .mail import ModerationTaskStateSubmissionEmailNotifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('/tmp/signals.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

# A marker for caching
NO_RECEIVERS = object()


def _make_id(target):
    if hasattr(target, '__func__'):
        return (id(target.__self__), id(target.__func__))
    return id(target)


NONE_ID = _make_id(None)


def receiver(signal, **kwargs):
    """
    A decorator for connecting receivers to signals. Used by passing in the
    signal (or list of signals) and keyword arguments to connect::

        @receiver(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs):
            ...

        @receiver([post_save, post_delete], sender=MyModel)
        def signals_receiver(sender, **kwargs):
            ...
    """

    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func

    return _decorator


class MySignal(Signal):
    """
    Base class for all signals

    Internal attributes:

        receivers
            { receiverkey (id) : weakref(receiver) }
    """

    def __init__(self, use_caching=False):
        """
        Create a new signal.
        """
        self.receivers = []
        self.lock = threading.Lock()
        self.use_caching = use_caching
        # For convenience we create empty caches even if they are not used.
        # A note about caching: if use_caching is defined, then for each
        # distinct sender we cache the receivers that sender has in
        # 'sender_receivers_cache'. The cache is cleaned when .connect() or
        # .disconnect() is called and populated on send().
        self.sender_receivers_cache = weakref.WeakKeyDictionary() if use_caching else {}
        self._dead_receivers = False

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        """
        Connect receiver to sender for signal.

        Arguments:

            receiver
                A function or an instance method which is to receive signals.
                Receivers must be hashable objects.

                If weak is True, then receiver must be weak referenceable.

                Receivers must be able to accept keyword arguments.

                If a receiver is connected with a dispatch_uid argument, it
                will not be added if another receiver was already connected
                with that dispatch_uid.

            sender
                The sender to which the receiver should respond. Must either be
                a Python object, or None to receive events from any sender.

            weak
                Whether to use weak references to the receiver. By default, the
                module will attempt to use weak references to the receiver
                objects. If this parameter is false, then strong references will
                be used.

            dispatch_uid
                An identifier used to uniquely identify a particular instance of
                a receiver. This will usually be a string, though it may be
                anything hashable.
        """
        from django.conf import settings

        logger.debug(f'Moderation Connect Entered {receiver}')
        # If DEBUG is on, check that we got a good receiver
        if settings.configured and settings.DEBUG:
            if not callable(receiver):
                raise TypeError('Signal receivers must be callable.')
            # Check for **kwargs
            if not func_accepts_kwargs(receiver):
                raise ValueError('Signal receivers must accept keyword arguments (**kwargs).')

        if dispatch_uid:
            lookup_key = (dispatch_uid, _make_id(sender))
        else:
            lookup_key = (_make_id(receiver), _make_id(sender))

        if weak:
            ref = weakref.ref
            receiver_object = receiver
            # Check for bound methods
            if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
                ref = weakref.WeakMethod
                receiver_object = receiver.__self__
            receiver = ref(receiver)
            weakref.finalize(receiver_object, self._remove_receiver)

        with self.lock:
            self._clear_dead_receivers()
            if not any(r_key == lookup_key for r_key, _ in self.receivers):
                logger.debug(f'Moderation Added Receiver {receiver}')
                self.receivers.append((lookup_key, receiver))
            self.sender_receivers_cache.clear()

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None):
        """
        Disconnect receiver from sender for signal.

        If weak references are used, disconnect need not be called. The receiver
        will be removed from dispatch automatically.

        Arguments:

            receiver
                The registered receiver to disconnect. May be none if
                dispatch_uid is specified.

            sender
                The registered sender to disconnect

            dispatch_uid
                the unique identifier of the receiver to disconnect
        """
        logger.debug(f'Moderation Disconnect Entered {receiver}:{sender}:{dispatch_uid}')
        if dispatch_uid:
            lookup_key = (dispatch_uid, _make_id(sender))
        else:
            lookup_key = (_make_id(receiver), _make_id(sender))

        disconnected = False
        with self.lock:
            self._clear_dead_receivers()
            for index in range(len(self.receivers)):
                (r_key, _) = self.receivers[index]
                if r_key == lookup_key:
                    disconnected = True
                    del self.receivers[index]
                    break
            self.sender_receivers_cache.clear()
        logger.debug(f'Moderation Disconnect {disconnected}')
        return disconnected

    def has_listeners(self, sender=None):
        return bool(self._live_receivers(sender))

    def send(self, sender, **named):
        """
        Send signal from sender to all connected receivers.

        If any receiver raises an error, the error propagates back through send,
        terminating the dispatch loop. So it's possible that all receivers
        won't be called if an error is raised.

        Arguments:

            sender
                The sender of the signal. Either a specific object or None.

            named
                Named arguments which will be passed to receivers.

        Return a list of tuple pairs [(receiver, response), ... ].
        """
        logger.debug('Moderation Send Entered')
        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            logger.debug('Moderation Send returning []')
            return []

        ret = [(receiver, receiver(signal=self, sender=sender, **named)) for receiver in self._live_receivers(sender)]
        logger.debug(f'Moderation Send returning {ret}')
        return ret

    def send_robust(self, sender, **named):
        """
        Send signal from sender to all connected receivers catching errors.

        Arguments:

            sender
                The sender of the signal. Can be any Python object (normally one
                registered with a connect if you actually want something to
                occur).

            named
                Named arguments which will be passed to receivers.

        Return a list of tuple pairs [(receiver, response), ... ].

        If any receiver raises an error (specifically any subclass of
        Exception), return the error instance as the result for that receiver.
        """
        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            return []

        # Call each receiver with whatever arguments it can accept.
        # Return a list of tuple pairs [(receiver, response), ... ].
        responses = []
        for receiver in self._live_receivers(sender):
            try:
                response = receiver(signal=self, sender=sender, **named)
            except Exception as err:
                logger.error(
                    'Error calling %s in Signal.send_robust() (%s)',
                    receiver.__qualname__,
                    err,
                    exc_info=err,
                )
                responses.append((receiver, err))
            else:
                responses.append((receiver, response))
        return responses

    def _clear_dead_receivers(self):
        # Note: caller is assumed to hold self.lock.
        if self._dead_receivers:
            self._dead_receivers = False
            self.receivers = [
                r for r in self.receivers if not (isinstance(r[1], weakref.ReferenceType) and r[1]() is None)
            ]

    def _live_receivers(self, sender):
        """
        Filter sequence of receivers to get resolved, live receivers.

        This checks for weak references and resolves them, then returning only
        live receivers.
        """
        receivers = None
        if self.use_caching and not self._dead_receivers:
            receivers = self.sender_receivers_cache.get(sender)
            # We could end up here with NO_RECEIVERS even if we do check this case in
            # .send() prior to calling _live_receivers() due to concurrent .send() call.
            if receivers is NO_RECEIVERS:
                return []
        if receivers is None:
            with self.lock:
                self._clear_dead_receivers()
                senderkey = _make_id(sender)
                receivers = []
                for (receiverkey, r_senderkey), receiver in self.receivers:
                    if r_senderkey == NONE_ID or r_senderkey == senderkey:
                        receivers.append(receiver)
                if self.use_caching:
                    if not receivers:
                        self.sender_receivers_cache[sender] = NO_RECEIVERS
                    else:
                        # Note, we must cache the weakref versions.
                        self.sender_receivers_cache[sender] = receivers
        non_weak_receivers = []
        for receiver in receivers:
            if isinstance(receiver, weakref.ReferenceType):
                # Dereference the weak reference.
                receiver = receiver()
                if receiver is not None:
                    non_weak_receivers.append(receiver)
            else:
                non_weak_receivers.append(receiver)
        return non_weak_receivers

    def _remove_receiver(self, receiver=None):
        # Mark that the self.receivers list has dead weakrefs. If so, we will
        # clean those up in connect, disconnect and _live_receivers while
        # holding self.lock. Note that doing the cleanup here isn't a good
        # idea, _remove_receiver() will be called as side effect of garbage
        # collection, and so the call can happen while we are already holding
        # self.lock.
        self._dead_receivers = True


def register_signal_handlers():
    logger.debug('register_signal_handlers() entered')
    group_approval_email_notifier = GroupApprovalTaskStateSubmissionEmailNotifier()
    workflow_submission_email_notifier = WorkflowStateSubmissionEmailNotifier()

    stat = task_submitted.disconnect(
        group_approval_email_notifier,
        sender=TaskState,
        dispatch_uid='group_approval_task_submitted_email_notification',
    )
    logger.debug(f'task_submission_email_notifier: {stat}')
    stat = workflow_submitted.disconnect(
        workflow_submission_email_notifier,
        sender=WorkflowState,
        dispatch_uid='workflow_state_submitted_email_notification',
    )

    logger.debug(f'workflow_submission_email_notifier: {stat}')
    task_submission_email_notifier = ModerationTaskStateSubmissionEmailNotifier(
        (
            TaskState,
            WorkflowState,
        )
    )
    my_signal = MySignal()
    task_submitted.send = my_signal.send
    task = Task()
    my_task = MyTask()
    task.start = my_task.start
    my_signal.connect(receiver=task_submission_email_notifier, sender=TaskState, dispatch_uid='my-unique-identifier')
    logger.debug('register_signal_handlers() exited')


class MyTask(Task):
    class Meta:
        managed = False

    def start(self, workflow_state, user=None):
        """Start this task on the provided workflow state by creating an instance of TaskState"""
        logger.debug('MyTask: start entered')
        task_state = self.get_task_state_class()(workflow_state=workflow_state)
        task_state.status = TaskState.STATUS_IN_PROGRESS
        task_state.revision = workflow_state.content_object.get_latest_revision()
        task_state.task = self
        task_state.save()
        logger.debug(f'MyTask: sending signal {task_state.specific.__class__}:{task_state.specific}')
        task_submitted.send(
            sender=task_state.specific.__class__,
            instance=task_state.specific,
            user=user,
        )

        logger.debug('MyTask: start exiting')
        return task_state
