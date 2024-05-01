import sqlalchemy_easy_softdelete.mixin
from datetime import datetime


class SoftDeleteMixin(
    sqlalchemy_easy_softdelete.mixin.generate_soft_delete_mixin_class()
):
    deleted_at: datetime