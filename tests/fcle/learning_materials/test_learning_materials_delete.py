# TODO: Узнать где обращение к ресурсу

# import pytest

# from settings import (
#     OK, UNAUTHORIZED
# )

# from fixtures.learning_materials.fixture_learning_materials import (
#     learning_materials,
#     add_material_and_get_id,
# )

# @pytest.mark.parametrize(
#     "expected_status_code",
#     (
#         (OK, ),
#         (UNAUTHORIZED, )
#     )
# )
# @pytest.mark.learning_materials
# class TestLearningMaterialsDelete:

#     @pytest.fixture(autouse=True)
#     def setup(self, learning_materials):
#         """
#         AUTOUSED FIXTURE: Sets up test environment before each test method.

#         Args:
#             learning_materials: API client fixture for LearningMaterials endpoints
#         """
#         self.client = learning_materials

#     def test_delete(
#             self,
#             add_material_and_get_id,
#             expected_status_code,
#             ):

#         _, material_id = add_material_and_get_id()

#         if UNAUTHORIZED in expected_status_code:
#             self.client.headers = {}

#         response = self.client.delete(material_id)

#         assert response.status_code in expected_status_code, (
#         f"{response.status_code}",
#         f"{response.text}",
#         )

#     @pytest.mark.parametrize(
#         "case",
#         (
#             "materialType 1 with jpg",
#         )
#     )
#     def test_delete_picture(
#             self,
#             add_material_and_get_id,
#             expected_status_code,
#             case
#     ):
#         _, material_id = add_material_and_get_id(case=case)

#         if UNAUTHORIZED in expected_status_code:
#             self.client.headers = {}

#         response = self.client.delete_picture(material_id)

#         assert response.status_code in expected_status_code, (
#         f"{response.status_code}",
#         f"{response.text}",
#         )
