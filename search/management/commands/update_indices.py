from django.core.exceptions import FieldError
from wagtail.search.backends import get_search_backend
from wagtail.search.index import get_indexed_models
from wagtail.search.management.commands.update_index import (
    Command as WagtailCommand,
    group_models_by_index,
)

DEFAULT_CHUNK_SIZE = 1000


class Command(WagtailCommand):

    def exclude_tags(self, qs):
        """
        Used to exclude models with meta_robots_nofollow=True and meta_robots_noindex=True
        """
        for model in qs:
            qs = model.get_indexed_objects()
            try:
                qs.exclude(meta_robots_nofollow=True, meta_robots_noindex=True)
            except FieldError:
                pass
        return qs.order_by('pk')

    def add_object(self, models, index, backend_name, schema_only=False, chunk_size=DEFAULT_CHUNK_SIZE):
        object_count = 0
        if not schema_only:
            for model in models:
                self.write(f'{backend_name}: {model._meta.app_label}.{model.__name__}'.ljust(35), ending='')

                # modify the qs before chunking
                qs = self.exclude_tags(model.get_indexed_objects())

                # Add items (chunk_size at a time)
                for chunk in self.print_iter_progress(self.queryset_chunks(qs, chunk_size)):
                    index.add_items(model, chunk)
                    object_count += len(chunk)

                self.print_newline()
        return object_count

    def update_backend(self, backend_name, schema_only=False, chunk_size=DEFAULT_CHUNK_SIZE):
        self.write('Updating backend: ' + backend_name)

        backend = get_search_backend(backend_name)

        if not backend.rebuilder_class:
            self.write("Backend '%s' doesn't require rebuilding" % backend_name)
            return

        models_grouped_by_index = group_models_by_index(backend, get_indexed_models()).items()
        if not models_grouped_by_index:
            self.write(backend_name + ': No indices to rebuild')

        for index, models in models_grouped_by_index:
            self.write(backend_name + ': Rebuilding index %s' % index.name)

            # Start rebuild
            rebuilder = backend.rebuilder_class(index)
            index = rebuilder.start()

            # Add models
            for model in models:
                index.add_model(model)

            # Add objects
            object_count = self.add_object(models, index, backend, schema_only, chunk_size)

            # Finish rebuild
            rebuilder.finish()

            self.write(backend_name + ': indexed %d objects' % object_count)
            self.print_newline()
