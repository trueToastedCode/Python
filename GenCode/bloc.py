import pyperclip


def gen_state(name, states):
    str = f'part of \'{name.lower()}_bloc.dart\';\n\nabstract class {name}State extends Equatable ' + '{\n'
    str += f'  const {name}State();\n'

    for state in states:
        if 'Subscriped' in state:
            continue
        str += f'  factory {name}State.{state.lower()}()\n      => {name}{state}State();\n'

    str += '\n  @override\n  List<Object> get props => [];\n' + '}\n\n'

    for state in states:
        if 'Subscriped' in state:
            continue
        str += f'class {name}{state}State extends {name}State ' + '{\n'
        str += f'  const {name}{state}State(' + ');\n\n  @override\n  List<Object> get props => [];\n}\n\n'

    str = str[:-1]
    return str


def gen_event(name, states):
    str = f'part of \'{name.lower()}_bloc.dart\';\n\nabstract class {name}Event extends Equatable ' + '{\n'
    str += f'  const {name}Event();\n'

    for state in states:
        str += f'  factory {name}Event.{state.lower()}()\n      => {name}{state}Event();\n'

    str += '\n  @override\n  List<Object> get props => [];\n' + '}\n\n'

    for state in states:
        str += f'class {name}{state}Event extends {name}Event ' + '{\n'
        str += f'  const {name}{state}Event(' + ');\n\n  @override\n  List<Object> get props => [];\n}\n\n'

    str = str[:-1]
    return str


def gen_bloc(name, states):
    str = f'part \'{name.lower()}_event.dart\';\npart \'{name.lower()}_state.dart\';\n\nclass {name}Bloc extends Bloc<{name}Event, {name}State>' + '{\n'
    str += f'  StreamSubscription? _subscription;\n\n  {name}Bloc() : super({name}State.{states[0].lower()}());\n\n'
    str += f'  @override\n  Stream<{name}State> mapEventToState({name}Event event) async* ' + '{\n'

    for state in states:
        if 'Subscriped' in state:
            str += f'    if (event is {name}{state}Event) ' + '{\n'
            str += '      await _subscription?.cancel();\n'
            str += '      _subscription = SOURCE.SOURCE()\n'
            str += '          .listen((OBJECT) => add(EVENT())));\n' + '    }\n\n'
        else:
            str += f'    if (event is {name}{state}Event) ' + '{\n'
            str += f'      yield {name}State.{state.lower()}();\n' + '    }\n\n'
    str = str[:-1] + '  }\n\n'

    str += '  @override\n  Future<void> close() {\n    _subscription?.cancel();\n  return super.close();\n  }\n}'

    return str

name = 'Message'
states = ['Initial', 'Subscriped', 'MessageReceive']

# text = gen_state(name, states)

# text = gen_event(name, states)

text = gen_bloc(name, states)

pyperclip.copy(text)
