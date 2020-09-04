from bson import ObjectId
from django.db import connections

from oclapi.utils import remove_from_search_index
from oclapi.utils import update_search_index_by_id
from tasks import update_search_index_task


class RawQueries():

    db = connections['default']

    def bulk_delete(self, type, ids):
        collection = self.db.get_collection(type._meta.db_table)
        collection.remove({'_id': {'$in': [ObjectId(id) for id in ids]}})
        for id in ids:
            remove_from_search_index(type, id)

    def bulk_delete_from_list(self, type, ids, list_field, list_values):
        collection = self.db.get_collection(type._meta.db_table)
        collection.update({'_id': {'$in': [ObjectId(id) for id in ids]}}, {'$pull': {list_field: {'$in': list_values}}})
        for id in ids:
            update_search_index_by_id(type, id)

    def find_by_id(self, type, id):
        collection = self.db.get_collection(type._meta.db_table)
        item = collection.find_one({'_id': ObjectId(id)})
        return item

    def find_by_field(self, type, field, value):
        collection = self.db.get_collection(type._meta.db_table)
        items = collection.find({field: value})
        return items

    def delete_source_version(self, source_version):

        from mappings.models import MappingVersion
        mapping_version_ids = list(source_version.get_mapping_ids()) #store before deletion

        MappingVersion.objects.raw_update({}, {'$pull': {'source_version_ids': source_version.id}})

        update_search_index_task.delay(MappingVersion, MappingVersion.objects.filter(id__in=mapping_version_ids))

        from concepts.models import ConceptVersion
        concept_versions_ids = list(source_version.get_concept_ids()) #store before deletion

        ConceptVersion.objects.raw_update({}, {'$pull': {'source_version_ids': source_version.id}})

        update_search_index_task.delay(ConceptVersion, ConceptVersion.objects.filter(id__in=concept_versions_ids))


    def delete_source(self, source):
        from sources.models import SourceVersion
        source_version_ids = list(SourceVersion.objects.filter(versioned_object_id=source.id).values_list('id', flat=True))

        from mappings.models import Mapping
        mapping_ids = list(Mapping.objects.filter(parent_id=source.id).values_list('id', flat=True))

        #Note that some MappingVersions may have been detached from all SourceVersions thus using versioned_object_id to delete
        from mappings.models import MappingVersion
        mapping_version_ids = list(MappingVersion.objects.filter(versioned_object_id__in=mapping_ids).values_list('id', flat=True))
        MappingVersion.objects.filter(versioned_object_id__in=mapping_ids).delete()
        for mapping_version_id in mapping_version_ids:
            remove_from_search_index(MappingVersion, mapping_version_id)

        Mapping.objects.filter(parent_id=source.id).delete()
        for mapping_id in mapping_ids:
            remove_from_search_index(Mapping, mapping_id)

        from concepts.models import Concept
        concept_ids = list(Concept.objects.filter(parent_id=source.id).values_list('id', flat=True))

        #Note that some ConceptVersions may have been detached from all SourceVersions thus using versioned_object_id to delete
        from concepts.models import ConceptVersion
        concept_version_ids = list(ConceptVersion.objects.filter(versioned_object_id__in=concept_ids).values_list('id', flat=True))
        ConceptVersion.objects.filter(versioned_object_id__in=concept_ids).delete()
        for concept_version_id in concept_version_ids:
            remove_from_search_index(ConceptVersion, concept_version_id)

        Concept.objects.filter(parent_id=source.id).delete()
        for concept_id in concept_ids:
            remove_from_search_index(Concept, concept_id)

        SourceVersion.objects.filter(versioned_object_id=source.id).delete()
        for source_version_id in source_version_ids:
            remove_from_search_index(SourceVersion, source_version_id)

        from sources.models import Source
        Source.objects.filter(id=source.id).delete()
        remove_from_search_index(Source, source.id)
