import csv
import click
from lark import Lark

branch_parser = Lark(r"""
    branch_rule: [ambiguous_part]

    var : "[" TOKEN ("(" INT ")")*"]"

    ambiguous_part : part | bracketed_part | pair

    bracketed_part : "(" part ")"

    part : ambiguous_part (JUNCTION ambiguous_part)*
    pair : var COMPARATOR VALUE

    %import common.WS
    %import common.INT
    %ignore WS

    TOKEN: /_?[A-Za-z][_A-Za-z0-9]*/

    COMPARATOR : ">=" | "<=" | "="
    JUNCTION : "and" | "or"

    STRING_VALUE : QUOTE /.*?/ QUOTE
    VALUE : STRING_VALUE | INT

    QUOTE : "'" | "\""

""", start='branch_rule'
)


@click.command()
@click.argument('filename', type=click.Path(exists=True, readable=True), nargs=1)

def main(filename):
    with open(filename, 'r') as csvfile:
        datareader = csv.DictReader(csvfile)
        for row in datareader:
            try:
                bl = row['Branching Logic (Show field only if...)']

                x = branch_parser.parse(bl)
            except Exception as e:
                fn = row['Form Name']
                sh = row['Section Header']
                fl = row['Field Label']

                print(f'{fn} > {sh} > {fl}')
                print(e)

main()
