from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate


class CRUDTestCase(CRUDBase[TestCase, TestCaseCreate, TestCaseUpdate]):
    def get_multi_by_scope(
        self,
        db: Session,
        *,
        project_id: int | None = None,
        module_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestCase]:
        query = db.query(self.model)
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        if module_id is not None:
            query = query.filter(self.model.module_id == module_id)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()


test_case = CRUDTestCase(TestCase)
