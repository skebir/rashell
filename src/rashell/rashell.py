import sys

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from rich import print
from rich.text import Text
from textx import TextXError

from rashell.relational_engine import RelationalEngine


def main():
    engine = RelationalEngine()
    if len(sys.argv) > 1:
        try:
            engine.open_from_file(sys.argv[1])
        except TextXError as e:
            sys.exit('Line {}: {}'.format(e.line, e.message))
        except Exception as e:
            sys.exit(str(e))

    bindings = KeyBindings()

    @bindings.add("f3")
    def _(event):
        session.multiline = not session.multiline

    def get_bottom_toolbar():
        multiline_hint = '<b>[F3]</b> Multiline: <b>{}</b>'.format(
            '<style bg="ansigreen">ON</style> (<i>alt-enter to run</i>)' if session.multiline else '<style bg="ansired">OFF</style> (<i>enter to run</i>)'
        )
        operations_hint = '<b>[TAB]</b> Operations'

        return HTML(' | '.join([operations_hint, multiline_hint]))

    operation_completer = WordCompleter(
        words=["⋈", "σ", "π", "U", "∩", "-", "X"],
        meta_dict={
            "⋈": HTML('Join <style fg="ansigray">(<b>Syntax:</b> <i>R</i> ⋈ <i>S</i> | <i>condition</i>)</style>'),
            "σ": HTML('Restriction <style fg="ansigray">(<b>Syntax:</b> σ <i>condition</i> (<i>R</i>))</style>'),
            "π": HTML('Projection <style fg="ansigray">(<b>Syntax:</b> π <i>columns</i> (<i>R</i>))</style>'),
            "U": HTML('Union <style fg="ansigray">(<b>Syntax:</b> <i>R</i> U <i>S</i>)</style>'),
            "∩": HTML('Intersection <style fg="ansigray">(<b>Syntax:</b> <i>R</i> ∩ <i>S</i>)</style>'),
            "-": HTML('Difference <style fg="ansigray">(<b>Syntax:</b> <i>R</i> - <i>S</i>)</style>'),
            "X": HTML('Cartesian Product <style fg="ansigray">(<b>Syntax:</b> <i>R</i> X <i>S</i>)</style>'),
        },
        ignore_case=True,
    )

    session = PromptSession(
                '>>> ',
                multiline=True,
                key_bindings=bindings,
                completer=operation_completer,
                complete_while_typing=False,
                bottom_toolbar=get_bottom_toolbar)


    print("Welcome to [b]rashell[/], an interactive [b]r[/]elational [b]a[/]lgebra [b]shell[/]")
    print(Text("Author: Salim Kebir <s.kebir@esti-annaba.dz>"))
    print(Text("GitHub: https://github.com/skebir/rashell"))
    if engine.relations:
        engine.print_model('.model')
    while True:
        try:
            text = session.prompt()
            engine.instruction_mm.model_from_str(text)
        except KeyboardInterrupt:
            continue
        except EOFError:
            sys.exit('Goodbye!')
        except Exception as e:
            print(f'[bold red]{e}[/]')


if __name__ == '__main__':
    main()
