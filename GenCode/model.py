import pyperclip


def gen_model(class_name, attributes):
    str = 'class ' + class_name + """ {
  String? get id => _id;
  late final String _id;
"""
    for attribute in attributes:
        str += f'  final String {attribute};\n'
    str += '\n'

    str += '  ' + class_name + '({\n'
    for attribute in attributes:
        str += f'    required this.{attribute},\n'
    str = str[:-2] + '\n  });\n\n'

    str += '  toJson() => {\n'
    for attribute in attributes:
        str += f'    \'{attribute}\': {attribute},\n'
    str = str[:-2] + '\n  };\n\n'

    str += '  factory ' + class_name + '.fromJson(Map<String, dynamic> json) {\n' \
           f'    final {class_name[0].lower() + class_name[1:]} = {class_name}(\n'
    for attribute in attributes:
        str += f'        {attribute}: json[\'{attribute}\'],\n'
    str = str[:-2] + ');\n' \
          f'    {class_name[0].lower() + class_name[1:]}._id = json[\'id\'];\n' \
          f'    return {class_name[0].lower() + class_name[1:]};\n' \
          '  }\n'

    str += '}'
    return str


text = gen_model('Message', ['teacher', 'user', 'data', 'upVotes', 'downVotes'])
pyperclip.copy(text)
