QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'text': f'Text {i}',
    } for i in range(12)
]

ANSWERS = [
    {
        'id': i,
        'text': f'Text {i}',
        'correct': i / 5 < 0.5,
    } for i in range(5)
]

USER = {
    'status': True,
}

POPULAR_TAGS = [
    {
        'tag_name': f'tag_{i}',
    } for i in range(15)
]

QUESTION_TAGS = [
    {
        'tag_name': f'tag_{i}',
    } for i in range(4)
]