import json
import hashlib

file_local_swagger = open("local-swagger.json", "r")
file_remote_swagger = open("remote-swagger.json", "r")
file_swagger_mess = open("api-docs-mess.json", "r")

jsonLocal = json.loads(file_local_swagger.read())
jsonRemote = json.loads(file_remote_swagger.read())
jsonMess = json.loads(file_swagger_mess.read())


def add_hash_in_swagger_obj(swagger_json):
    swagger_json = do_hash_paths(swagger_json)
    swagger_json = do_hash_definitions(swagger_json)
    return swagger_json


def do_hash_paths(swagger_json):
    for k in swagger_json['paths']:
        for method in swagger_json['paths'][k]:
            swagger_json['paths'][k][method] = remove_operation_id(swagger_json['paths'][k][method])
            swagger_json['paths'][k][method] = add_hash_attribute(swagger_json['paths'][k][method])
        swagger_json['paths'][k] = add_hash_attribute(swagger_json['paths'][k])
    return swagger_json


def do_hash_definitions(swagger_json):
    for k in swagger_json['definitions']:
        swagger_json['definitions'][k] = add_hash_attribute(swagger_json['definitions'][k])
    return swagger_json


def add_hash_attribute(obj):
    hash_me = json.dumps(obj)
    obj['hash'] = hashlib.md5(hash_me.encode()).hexdigest()
    return obj


def remove_operation_id(obj):
    if "operationId" in obj:
        obj.pop("operationId", None)
    return obj


def compare_swagger(section, message, new_obj, old_obj, paths=False):
    new = new_obj[section]
    old = old_obj[section]
    message = compare(section.title(), message, new, old, paths)
    return message


def compare(title, message, new, old, paths=False, method=False):

    _INDENT_ = 4
    _BULLET_ = "-"
    if method:
        _INDENT_ = _INDENT_ * 1.5
        _BULLET_ = "*"

    if paths is True and method is False:
        make_title(message, new, old, title)
        message.append("## {} ".format(title))
    elif paths is False and method is False:
        make_title(message, new, old, title)
        message.append("## {} ".format(title))

    for attr in new:
        if attr in old:
            if type(new[attr]) is dict:
                if new[attr]['hash'] != old[attr]['hash']:
                    message.append("{0:>{indent}}{bullet} {status:16}: {attr}"
                                   .format(" ", indent=_INDENT_, status="Modified", attr=attr, bullet=_BULLET_))

                # Special Case for Paths
                if paths:
                    compare("Methods", message, new[attr], old[attr], False, True)

        elif attr not in old:
            if type(new[attr]) is dict:
                message.append("{0:>{indent}}{bullet} {status:16}: {attr}"
                               .format(" ", indent=_INDENT_, status="New", attr=attr, bullet=_BULLET_))
    for attr in old:
        if attr not in new:
            if type(old[attr]) is dict:
                message.append("{0:>{indent}}{bullet} {status:16}: {attr}"
                               .format(" ", indent=_INDENT_, status="Removed", attr=attr, bullet=_BULLET_))

    return message


def make_title(message, new, old, title):
    if new == old:
        message.append("""
==========================================================================
# New Swagger {} and Old Swagger {} are same
==========================================================================
    """.format(title, title))
    else:
        message.append("""
==========================================================================
# New Swagger {} and Old Swagger {} are not same
==========================================================================
        """.format(title, title))
    return message


def do_compare_swagger(new_swagger, old_swagger):
    message = []
    message = compare_swagger('paths', message, new_swagger, old_swagger, True)
    message = compare_swagger('definitions', message, new_swagger, old_swagger)
    return message


newSwagger = add_hash_in_swagger_obj(jsonLocal)
oldSwagger = add_hash_in_swagger_obj(jsonRemote)

r = do_compare_swagger(newSwagger, oldSwagger)
for i in r:
    print(i)

# print("")
# print(json.dumps(newSwagger['paths']['/v1/agent']['get'], sort_keys=True))
# print(json.dumps(oldSwagger['paths']['/v1/agent']['get'], sort_keys=True))
