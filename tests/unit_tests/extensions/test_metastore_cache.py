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

from uuid import UUID

from flask import Flask
from pytest_mock import MockerFixture

from superset.extensions.metastore_cache import SupersetMetastoreCache
from superset.key_value.types import JsonKeyValueCodec, PickleKeyValueCodec

NAMESPACE = UUID("ee173d1b-ccf3-40aa-941c-985c15224496")


def test_factory_defaults_to_json_codec(app: Flask) -> None:
    cache = SupersetMetastoreCache.factory(app, {}, [], {})
    assert isinstance(cache, SupersetMetastoreCache)
    assert isinstance(cache.codec, JsonKeyValueCodec)


def test_factory_honors_explicit_codec(app: Flask) -> None:
    codec = PickleKeyValueCodec()
    cache = SupersetMetastoreCache.factory(app, {"CODEC": codec}, [], {})
    assert isinstance(cache, SupersetMetastoreCache)
    assert cache.codec is codec


def test_get_treats_legacy_pickle_entry_as_miss(mocker: MockerFixture) -> None:
    entry = mocker.MagicMock()
    entry.is_expired.return_value = False
    entry.value = PickleKeyValueCodec().encode({"foo": "bar"})
    mocker.patch(
        "superset.daos.key_value.KeyValueDAO.get_entry",
        return_value=entry,
    )
    cache = SupersetMetastoreCache(namespace=NAMESPACE, codec=JsonKeyValueCodec())

    assert cache.get("foo") is None
    assert cache.has("foo") is False


def test_get_decodes_json_entry(mocker: MockerFixture) -> None:
    entry = mocker.MagicMock()
    entry.is_expired.return_value = False
    entry.value = JsonKeyValueCodec().encode({"foo": "bar"})
    mocker.patch(
        "superset.daos.key_value.KeyValueDAO.get_entry",
        return_value=entry,
    )
    cache = SupersetMetastoreCache(namespace=NAMESPACE, codec=JsonKeyValueCodec())

    assert cache.get("foo") == {"foo": "bar"}
