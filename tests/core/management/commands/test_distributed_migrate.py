from unittest.mock import call, patch

from django.core.management import call_command


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration_lock_acquired(
    mocked_advisory_lock, mocked_handle
):
    call_command('distributed_migrate')
    assert mocked_handle.call_count == 1
    assert mocked_advisory_lock.call_args == call(
        lock_id='migrations', wait=False,
    )


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration_lock_not_acquired(
    mocked_advisory_lock, mocked_handle
):
    mocked_advisory_lock.return_value.__enter__.side_effect = [False, True]
    call_command('distributed_migrate')
    assert mocked_handle.call_count == 0
    assert mocked_advisory_lock.call_count == 2
