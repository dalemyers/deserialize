
Unhandled Fields
----------------

Usually, if you don't specify the field in your definition, but it does exist in the data, you just want to ignore it. Sometimes however, you want to know if there is extra data. In this case, when calling `deserialize(...)` you can set `throw_on_unhandled=True` and it will raise an exception if any fields in the data are unhandled.

Additionally, sometimes you want this, but know of a particular field that can be ignored. You can mark these as allowed to be unhandled with the decorator `@allow_unhandled("key_name")`.
