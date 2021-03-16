STUDENT_ID_PARAM = 'studentId'

USER_ID = 'Id_Usuario'
FINISHED_DATE = 'Fecha_de_Finalizacion'
FREE_COURSES_COUNT = 'sum(Cursos_Obligatorios)'
MANDATORY_COURSES = 'sum(Cursos_Libres)'
COMPANY_ID = 'Id_Empresa'

STUDENT_QUERY_BY_USERID = "select concat_ws(' ', firstname, lastname) as name from mdl_user where id = '{student_id}'"
