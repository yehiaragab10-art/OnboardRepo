import warnings

from tree_sitter import Parser
from tree_sitter_languages import get_language

warnings.filterwarnings("ignore", category=FutureWarning)

source = """
class User:
    def save(self):
        pass

def helper():
    pass
"""

def print_node(node, indent=0):
    pad = "  " * indent
    print(
        f"{pad}{node.type} | "
        f"start={node.start_point} end={node.end_point} | "
        f"text={node.text.decode('utf-8', errors='ignore')[:30]}"
    )

    for child in node.children:
        print_node(child, indent + 1)


language = get_language("python")

parser = Parser()
parser.set_language(language)

tree = parser.parse(bytes(source, "utf8"))
root = tree.root_node

print("\n=== ROOT ===")
print_node(root)

print("\n=== TOP LEVEL ONLY ===\n")

lines = source.splitlines()

for child in root.children:
    start_line = child.start_point[0] + 1
    end_line = child.end_point[0] + 1

    extracted = "\n".join(lines[start_line-1:end_line])

    print(
        f"{child.type} | "
        f"{start_line=} {end_line=} | "
        f"EXTRACTED=\n{extracted}\n"
    )