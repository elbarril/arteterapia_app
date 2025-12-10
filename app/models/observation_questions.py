"""Observational questions configuration."""

# Answer options (plain strings - will be translated in templates)
ANSWER_OPTIONS = {
    'yes': 'Sí',
    'no': 'No',
    'not_sure': 'No está seguro/a',
    'not_applicable': 'No aplica'
}

# Hierarchical question structure  
OBSERVATION_CATEGORIES = [
    {
        'id': 'entry',
        'name': 'INGRESO AL ESPACIO',
        'questions': [
            {'id': 'entry_on_time', 'text': 'Llega a horario'},
            {'id': 'entry_resistance', 'text': 'Muestra resistencia'},
            {'id': 'entry_manages', 'text': 'Logra ingresar'},
            {'id': 'entry_greeting', 'text': 'Muestra indicador de saludo'},
        ]
    },
    {
        'id': 'motivation',
        'name': 'MOTIVACIÓN',
        'questions': [
            {'id': 'motivation_interest', 'text': 'Muestra interés'},
            {'id': 'motivation_rejection', 'text': 'Muestra rechazo'},
            {'id': 'motivation_repetition', 'text': 'Solicita o necesita repetición'},
        ]
    },
    {
        'id': 'instruction',
        'name': 'CONSIGNA',
        'questions': [
            {'id': 'instruction_keeps_mind', 'text': 'La mantiene en mente'},
            {'id': 'instruction_concentration', 'text': 'Mantiene la concentración'},
            {'id': 'instruction_requests_repetition', 'text': 'Solicita repetición'},
            {'id': 'instruction_reiterated', 'text': 'Se le reitera la consigna'},
            {'id': 'instruction_personal_emergent', 'text': 'Trae un emergente personal'},
        ]
    },
    {
        'id': 'development',
        'name': 'DESARROLLO',
        'subcategories': [
            {
                'id': 'development_beginning',
                'name': 'Inicio',
                'questions': [
                    {'id': 'dev_begin_interest', 'text': 'Muestra interés'},
                ]
            },
            {
                'id': 'development_time',
                'name': 'Tiempo',
                'questions': [
                    {'id': 'dev_time_indifferent', 'text': 'Se muestra indiferente'},
                    {'id': 'dev_time_delayed', 'text': 'Inicio demorado'},
                    {'id': 'dev_time_expected', 'text': 'Inicio esperado o establecido'},
                ]
            },
            {
                'id': 'development_materials',
                'name': 'Materiales',
                'questions': [
                    {'id': 'dev_mat_explores', 'text': 'Explora los materiales'},
                    {'id': 'dev_mat_innovative', 'text': 'Los utiliza de manera innovadora/creativa'},
                    {'id': 'dev_mat_repeats', 'text': 'Repite el mismo uso'},
                    {'id': 'dev_mat_needs_support', 'text': 'Necesita apoyo para utilizarlos'},
                    {'id': 'dev_mat_full_use', 'text': 'Hace uso pleno de ellos'},
                    {'id': 'dev_mat_difficulty', 'text': 'Muestra dificultad para manipularlos'},
                    {'id': 'dev_mat_asks_other', 'text': 'Pide otros materiales'},
                ]
            },
            {
                'id': 'development_creativity',
                'name': 'Creatividad',
                'questions': [
                    {'id': 'dev_cre_present', 'text': 'Está presente / conectado/a'},
                    {'id': 'dev_cre_focused', 'text': 'Se muestra concentrado/a y trabaja'},
                    {'id': 'dev_cre_tolerance', 'text': 'Muestra tolerancia a la frustración'},
                ]
            },
            {
                'id': 'development_space',
                'name': 'En el espacio',
                'questions': [
                    {'id': 'dev_space_asks_help', 'text': 'Pide ayuda'},
                    {'id': 'dev_space_communicates', 'text': 'Se comunica'},
                    {'id': 'dev_space_isolates', 'text': 'Se aísla'},
                    {'id': 'dev_space_helps_others', 'text': 'Ayuda a otros/as'},
                    {'id': 'dev_space_connection_at', 'text': 'Establece vínculo con el/la AT'},
                ]
            },
        ]
    },
    {
        'id': 'closure',
        'name': 'CIERRE',
        'questions': [
            {'id': 'closure_accepts', 'text': 'Acepta su propia producción'},
            {'id': 'closure_verbalizes', 'text': 'Pone en palabras lo producido'},
            {'id': 'closure_denotative', 'text': 'Hace asociaciones denotativas'},
            {'id': 'closure_connotative', 'text': 'Expresa asociaciones connotativas'},
            {'id': 'closure_mood_change', 'text': 'Muestra cambios de ánimo respecto del inicio'},
            {'id': 'closure_bodily_change', 'text': 'Muestra cambios de actitud corporal respecto del inicio'},
        ]
    },
    {
        'id': 'group',
        'name': 'GRUPO',
        'questions': [
            {'id': 'group_respects_turn', 'text': 'Respeta el turno de habla de los/as otros/as'},
            {'id': 'group_indifferent', 'text': 'Se muestra indiferente a la palabra de los/as otros/as'},
            {'id': 'group_waits_turn', 'text': 'Logra esperar su turno'},
            {'id': 'group_registers_presence', 'text': 'Registra la presencia de otras personas'},
            {'id': 'group_interacts', 'text': 'Interactúa con otros/as en el espacio'},
        ]
    },
    {
        'id': 'group_climate',
        'name': 'CLIMA GRUPAL',
        'questions': [
            {'id': 'climate_favorable', 'text': 'Favorable'},
            {'id': 'climate_disruptive', 'text': 'Disruptivo'},
            {'id': 'climate_indifferent', 'text': 'Indiferente'},
            {'id': 'climate_participatory', 'text': 'Participativo'},
        ]
    },
]


def get_all_questions():
    """
    Get a flat list of all questions with their category information.
    Returns list of dicts with keys: id, text, category_name, subcategory_name
    """
    questions = []
    
    for category in OBSERVATION_CATEGORIES:
        category_name = category['name']
        
        # Direct questions in category
        if 'questions' in category:
            for q in category['questions']:
                questions.append({
                    'id': q['id'],
                    'text': q['text'],
                    'category': category_name,
                    'subcategory': None
                })
        
        # Questions in subcategories
        if 'subcategories' in category:
            for subcat in category['subcategories']:
                subcat_name = subcat['name']
                for q in subcat['questions']:
                    questions.append({
                        'id': q['id'],
                        'text': q['text'],
                        'category': category_name,
                        'subcategory': subcat_name
                    })
    
    return questions


def get_question_by_index(index):
    """Get a specific question by its index in the flat list."""
    questions = get_all_questions()
    if 0 <= index < len(questions):
        return questions[index]
    return None


def get_total_question_count():
    """Get the total number of questions."""
    return len(get_all_questions())
