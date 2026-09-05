"""Print stable summaries of FBX geometry and skin bind data for comparison."""
import hashlib
import os
import sys


REPOSITORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPOSITORY)

from x4ue.fbx_export import parse_fbx


def digest(value):
    return hashlib.sha256(repr(value).encode("utf-8")).hexdigest()[:16]


def child_digest(element):
    return digest(element.props[0]) if element else "-"


def child(element, name):
    return next((item for item in element.elems if item.id == name), None)


def summarize(filepath):
    root, _version = parse_fbx.parse(filepath)
    objects = child(root, b"Objects")
    geometry_values = []
    bind_values = []
    model_values = []
    for element in objects.elems:
        if element.id == b"Geometry":
            vertices = child(element, b"Vertices")
            geometry_values.append((element.props[1], tuple(vertices.props[0])))
            coordinates = vertices.props[0]
            axes = tuple(coordinates[index::3] for index in range(3))
            print("GEOMETRY", element.props[1], len(coordinates) // 3,
                  tuple((min(axis), max(axis)) for axis in axes))
        elif element.id == b"Deformer" and element.props[2] == b"Cluster":
            transform = child(element, b"Transform")
            transform_link = child(element, b"TransformLink")
            indexes = child(element, b"Indexes")
            weights = child(element, b"Weights")
            bind_values.append((
                element.props[1],
                tuple(indexes.props[0]) if indexes else (),
                tuple(weights.props[0]) if weights else (),
                tuple(transform.props[0]) if transform else (),
                tuple(transform_link.props[0]) if transform_link else (),
            ))
        elif element.id == b"Model":
            model_values.append((
                element.props[1],
                tuple((item.id, tuple(item.props), bytes(item.props_type)) for item in element.elems),
            ))
    print("GEOMETRY_SUMMARY", len(geometry_values), digest(sorted(geometry_values)))
    print("BIND_SUMMARY", len(bind_values), digest(sorted(bind_values)))
    print("MODEL_SUMMARY", len(model_values), digest(sorted(model_values)))
    print("GEOMETRY_DATA", digest(sorted(value for _name, value in geometry_values)))
    print("BIND_DATA", digest(sorted(value[1:] for value in bind_values)))
    return geometry_values, bind_values


results = []
for argument in sys.argv[sys.argv.index("--") + 1:]:
    print("FILE", os.path.basename(argument))
    results.append(summarize(argument))

if len(results) == 2:
    _geometry_a, bind_a = results[0]
    _geometry_b, bind_b = results[1]
    for index, (cluster_a, cluster_b) in enumerate(zip(bind_a, bind_b)):
        if cluster_a[1:] != cluster_b[1:]:
            print("FIRST_BIND_DIFFERENCE", index, cluster_a[0])
            print("REFERENCE", [digest(value) for value in cluster_a[1:]])
            print("CURRENT", [digest(value) for value in cluster_b[1:]])
            print("REFERENCE_TRANSFORM", cluster_a[3])
            print("CURRENT_TRANSFORM", cluster_b[3])
            break
