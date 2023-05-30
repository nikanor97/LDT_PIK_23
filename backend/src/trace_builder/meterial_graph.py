import pandas as pd
from src.trace_builder.graph_models import Node, PipeGraph


def build_material_graph(material_graph: PipeGraph):
    common_counter = 1
    local_counter = 1
    is_first_in_branch = True
    rows = []
    for node in material_graph.nodes:
        if node.is_start:
            graph_value = f"A->{common_counter}"
        else:
            if node.is_end:
                letter = chr(node.uniq_end + ord("A"))
                graph_value = f"{local_counter}{letter}->{letter}"
                local_counter = 1
                is_first_in_branch = True
            elif node.is_inside_troinik:
                letter = chr(node.uniq_end + ord("A"))
                if is_first_in_branch:
                    first_letter = common_counter
                    second_letter = f"{local_counter}{letter}"
                    is_first_in_branch = False
                else:
                    first_letter = f"{local_counter}{letter}"
                    second_letter = f"{local_counter+1}{letter}"
                    local_counter += 1
                graph_value = f"{first_letter}->{second_letter}"
            else:
                graph_value = f"{common_counter}->{common_counter+1}"
                common_counter += 1
        length = int(node.length) if node.length else None
        rows.append(
            {"Граф": graph_value, "Материал": node.material_id, "Длина": length}
        )
    return pd.DataFrame.from_records(rows)
