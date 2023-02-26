
Raw Storage
-----------

It can sometimes be useful to keep a reference to the raw data that was used to construct an object. To do this, simply set the `raw_storage_mode` paramater to `RawStorageMode.ROOT` or `RawStorageMode.ALL`. This will store the data in a parameter named `__deserialize_raw__` on the root object, or on all objects in the tree respectively.
