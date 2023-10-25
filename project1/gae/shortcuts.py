
def get_objects_or_404(model, **kwargs):
    '''Return object with given criteria or show "page not found"'''
    collection = model.all()
    for filed_name, value in kwargs.items():
        collection = collection.filter(filed_name, value)
    return collection


def get_object_or_404(model, **kwargs):
    '''Return object with given key or show "page not found"'''
    if len(kwargs) < 1:
        raise Exception("Not specified filter conditions")
    try:
        if "key_name" in kwargs:
            obj = model.get_by_key_name(kwargs["key_name"])
        elif "id" in kwargs:
            obj = model.get_by_id(int(kwargs["id"]))
        elif "key" in kwargs:
            obj = model.get(kwargs["key"])
        else: # filter by multiple fields
            obj = get_objects_or_404(model, **kwargs)[0]
    except:
        obj = None
    if not obj:
        raise Exception("Object '%s' by arguments '%r' not found" %
                        (model.__name__, kwargs))
    return obj
