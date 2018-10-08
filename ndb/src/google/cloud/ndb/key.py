# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides a ``Key`` class for Google Cloud Datastore.

A Key encapsulates the following pieces of information, which together
uniquely designate a (possible) entity in Google Cloud Datastore:

* a Google Cloud Platform project (a string)
* an optional namespace (a string)
* a list of one or more (``kind``, ``id_``) pairs where ``kind`` is a string
  and ``id_`` is either a string or an integer
"""


import os

import google.cloud.datastore


__all__ = ["Key"]
_APP_ID_ENVIRONMENT = "APPLICATION_ID"
_APP_ID_DEFAULT = "_"


class Key:
    """An immutable datastore key.

    For flexibility and convenience, multiple constructor signatures are
    supported.

    The primary way to construct a key is using positional arguments:

    .. code-block:: python

        ndb.Key(kind1, id1, kind2, id2, ...)

    This is shorthand for either of the following two longer forms:

    .. code-block:: python

        ndb.Key(pairs=[(kind1, id1), (kind2, id2), ...])
        ndb.Key(flat=[kind1, id1, kind2, id2, ...])

    Either of the above constructor forms can additionally pass in another
    key using ``parent=<key>``. The ``(kind, id)`` pairs of the parent key are
    inserted before the ``(kind, id)`` pairs passed explicitly.

    You can also construct a Key from a "url-safe" encoded string:

    .. code-block:: python

        ndb.Key(urlsafe=<string>)

    For rare use cases the following constructors exist:

    .. code-block:: python

        # Passing in a low-level Reference object
        ndb.Key(reference=<reference>)
        # Passing in a serialized low-level Reference
        ndb.Key(serialized=<string>)
        # For unpickling, the same as ndb.Key(**<dict>)
        ndb.Key(<dict>)

    The "url-safe" string is really a websafe-base64-encoded serialized
    ``Reference``, but it's best to think of it as just an opaque unique
    string.

    If a ``Reference`` is passed (using one of the ``reference``,
    ``serialized`` or ``urlsafe`` keywords), the positional arguments and
    ``namespace`` must match what is already present in the ``Reference``
    (after decoding if necessary). The parent keyword cannot be combined with
    a ``Reference`` in any form.

    Keys are immutable, which means that a Key object cannot be modified
    once it has been created. This is enforced by the implementation as
    well as Python allows.

    For access to the contents of a key, the following methods and
    operations are supported:

    * ``repr(key)``, ``str(key)``: return a string representation resembling
      the shortest constructor form, omitting the app and namespace
      unless they differ from the default value
    * ``key1 == key2``, ``key1 != key2``: comparison for equality between keys
    * ``hash(key)``: a hash value sufficient for storing keys in a dictionary
    * ``key.pairs()``: a tuple of ``(kind, id)`` pairs
    * ``key.flat()``: a tuple of flattened kind and ID values, i.e.
      ``(kind1, id1, kind2, id2, ...)``
    * ``key.app()``: the Google Cloud Platform project (formerly called the
      application ID)
    * ``key.id()``: the string or integer ID in the last ``(kind, id)`` pair,
      or :data:`None` if the key is incomplete
    * ``key.string_id()``: the string ID in the last ``(kind, id)`` pair,
      or :data:`None` if the key has an integer ID or is incomplete
    * ``key.integer_id()``: the integer ID in the last ``(kind, id)`` pair,
      or :data:`None` if the key has a string ID or is incomplete
    * ``key.namespace()``: the namespace
    * ``key.kind()``: The "kind" of the key, from the last of the
      ``(kind, id)`` pairs
    * ``key.parent()``: a key constructed from all but the last ``(kind, id)``
      pairs. For example, the parent of
      ``[("Purchase", "Food"), ("Type", "Drink"), ("Coffee", 11)]`` is
      ``[("Purchase", "Food"), ("Type", "Drink")]``.
    * ``key.urlsafe()``: a websafe-base64-encoded serialized ``Reference``
    * ``key.serialized()``: a serialized ``Reference``
    * ``key.reference()``: a ``Reference`` object (the caller promises not to
      mutate it)

    Keys also support interaction with the datastore; these methods are
    the only ones that engage in any kind of I/O activity. For ``Future``
    objects, see the document for :mod:`google.cloud.ndb.tasklets`.

    * ``key.get()``: return the entity for the key
    * ``key.get_async()``: return a future whose eventual result is
      the entity for the key
    * ``key.delete()``: delete the entity for the key
    * ``key.delete_async()``: asynchronously delete the entity for the key

    Keys may be pickled.

    Subclassing Key is best avoided; it would be hard to get right.

    Args:
        path_args (Union[Tuple[str, ...], Tuple[Dict]]): Either a tuple of
            (kind, ID) pairs or a single dictionary containing only keyword
            arguments.
        reference (Optional[\
            ~google.cloud.datastore._app_engine_key_pb2.Reference]): A
            reference protobuf representing a key.
        serialized (Optional[bytes]): A reference protobuf serialized to bytes.
        urlsafe (Optional[str]): A reference protobuf serialized to bytes. The
            raw bytes are then converted to a websafe base64-encoded string.
        pairs (Optional[str]): An iterable of (kind, ID) pairs. If this
            argument is used, then ``path_args`` should be empty.
        flat (Optional[str]): An iterable of the (kind, ID) pairs but flattened
            into a single value. For example, the pairs
            ``[("Parent", 1), ("Child", "a")]`` would be flattened to
            ``["Parent", 1, "Child", "a"]``.
        app (Optional[str]): The Google Cloud Platform project (previously
            on Google App Engine, this was called the Application ID).
        namespace (Optional[str]): The namespace for the key.
        parent (Optional[~.ndb.key.Key]): The parent of the key being
            constructed. If provided, the key path will be **relative** to the
            parent key's path.
    """

    __slots__ = ("_key",)

    def __init__(
        self,
        *path_args,
        reference=None,
        serialized=None,
        urlsafe=None,
        pairs=None,
        flat=None,
        app=None,
        namespace=None,
        parent=None
    ):
        if reference is not None:
            raise NotImplementedError
        if serialized is not None:
            raise NotImplementedError
        if urlsafe is not None:
            raise NotImplementedError
        if pairs is not None:
            raise NotImplementedError
        if flat is not None:
            raise NotImplementedError
        if parent is not None:
            raise NotImplementedError

        project = _project_from_app(app)
        self._key = google.cloud.datastore.Key(
            *path_args, project=project, namespace=namespace
        )


def _project_from_app(app):
    """Convert a legacy Google App Engine app string to a project.

    Args:
        app (str): The application value to be used. If the caller passes
            :data:`None` then this will use the ``APPLICATION_ID`` environment
            variable to determine the running application.

    Returns:
        str: The cleaned project.
    """
    if app is None:
        app = os.environ.get(_APP_ID_ENVIRONMENT, _APP_ID_DEFAULT)

    # NOTE: This is the same behavior as in the helper
    #       ``google.cloud.datastore.key._clean_app()``.
    parts = app.split("~", 1)
    return parts[-1]