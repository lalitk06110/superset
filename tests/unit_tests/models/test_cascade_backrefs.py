# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Tests to verify cascade_backrefs=False is set on relationships that would
otherwise trigger SQLAlchemy 2.0 deprecation warnings (s9r1).
"""

import pytest
from sqlalchemy import inspect as sa_inspect


@pytest.mark.parametrize(
    "model_path,relationship_name",
    [
        ("superset.models.core.Database", "queries"),
        ("superset.models.core.Database", "saved_queries"),
        ("superset.models.core.Database", "tables"),
        ("superset.connectors.sqla.models.SqlaTable", "columns"),
        ("superset.connectors.sqla.models.SqlaTable", "metrics"),
        ("superset.tags.models.Tag", "objects"),
    ],
)
def test_cascade_backrefs_disabled(
    app_context: None, model_path: str, relationship_name: str
) -> None:
    """Relationships with cascade should set cascade_backrefs=False."""
    import importlib

    module_path, class_name = model_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    model_class = getattr(module, class_name)

    mapper = sa_inspect(model_class)
    rel = mapper.relationships[relationship_name]
    # In SQLAlchemy 2.0+ cascade_backrefs is removed (always False).
    # In 1.4 it must be explicitly False to suppress the deprecation warning.
    if hasattr(rel, "cascade_backrefs"):
        assert rel.cascade_backrefs is False, (
            f"{model_path}.{relationship_name} must set cascade_backrefs=False"
        )


def test_role_user_cascade_backrefs_disabled(app_context: None) -> None:
    """FAB's Role.user relationship should have cascade_backrefs=False."""
    from flask_appbuilder.security.sqla.models import Role

    mapper = sa_inspect(Role)
    rel = mapper.relationships["user"]
    if hasattr(rel, "cascade_backrefs"):
        assert rel.cascade_backrefs is False, (
            "Role.user must set cascade_backrefs=False"
        )
