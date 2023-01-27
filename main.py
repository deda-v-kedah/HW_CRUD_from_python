import psycopg2

from pprint import pprint



def create_db(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS 
                   users(user_id SERIAL PRIMARY KEY, first_name VARCHAR(60) NOT NULL, last_name VARCHAR(60) NOT NULL, email VARCHAR(60) NOT NULL);
                   
                   CREATE TABLE IF NOT EXISTS
                   phone(user_id INTEGER REFERENCES users (user_id), number VARCHAR(20));''')

    conn.commit()
    print('БД Создано')


def add_client(cur, first_name, last_name, email, phone=None):
    cur.execute('''INSERT INTO users(first_name, last_name, email)
                    VALUES(%s, %s, %s) RETURNING user_id;''', (first_name, last_name, email, ))

    user_id = cur.fetchone()[0]

    if phone != None:
        cur.execute('''INSERT INTO phone(user_id, number)
                    VALUES(%s, %s);''', (user_id, phone, ))      

    conn.commit()
    print(f'''Пользователь:
id: {user_id}
Фамилия: {first_name}
Имя: {last_name}
email: {email}
Телефон: {phone}
    
Успешно добавлен''')


def add_phone(cur, client_id, phone):
    cur.execute('''INSERT INTO phone(user_id, number)
                    VALUES(%s, %s);''', (client_id, phone, ))      

    conn.commit()
    print(f'Номер {phone} добавлен к пользователю: {client_id}')


def change_client(cur, client_id, first_name=None, last_name=None, email=None, phones=None):

    if first_name != None or last_name != None or email != None or phones != None:
        report = ''
        query_list = ''
        tuple_keys = ()

        if first_name != None:
            query_list = 'SET first_name = %s'
            tuple_keys += (first_name, ) 
            report += f'\nфамилию на {first_name}\n'

        if last_name != None:
            query_list += 'SET last_name = %s' if query_list == '' else ' , last_name = %s'
            tuple_keys += (last_name, )
            report += f'имя на {last_name}\n'

        if email != None:
            query_list += 'SET email = %s' if query_list == '' else ' , email = %s'
            tuple_keys += (email, )
            report += f'email на {email}\n'

        if phones != None:
            cur.execute( '''SELECT number FROM phone 
                            WHERE user_id = %s;''', (client_id, )) 
            select_list = cur.fetchall()
        
            if len(select_list) > 1:
                print('У данного клиента более одного номера, выберите который необходимо изменить')
                for i, phone_num in enumerate(select_list):
                    print(f'{i+1} - {phone_num[0]}')
                number_phone = int(input("Введите порядковый номер изменяемого номера: "))-1
                if number_phone+1 > len(select_list) or number_phone+1 < 1:
                    print('Нет такого')
                else:
                    cur.execute( '''UPDATE phone 
                        SET number = %s
                        WHERE user_id = %s AND number = %s;''', (phones, client_id, select_list[number_phone][0],))
                    conn.commit() 
                    report += f'телефон на {phones}'   
            elif len(select_list) == 0:
                print('Нет номеров')
            else:
                cur.execute( '''UPDATE phone 
                        SET number = %s
                        WHERE user_id = %s;''', (phones, client_id))

                conn.commit()
                report += f'телефон на {phones}'

        tuple_keys += (client_id,)


        if first_name != None or last_name != None or email != None:

            cur.execute( '''UPDATE users 
                            '''+query_list+'''
                            WHERE user_id = %s;''', tuple_keys)

            conn.commit()

        print(f'Пользователь {client_id} сменил: {report}')

    else:
        print('Не указаны изменяемые параметры')
        cur.execute( '''SELECT u.user_id, u.first_name, u.last_name, u.email, p.number FROM users u
                    LEFT JOIN phone p ON u.user_id = p.user_id 
                    WHERE u.user_id = %s
                    ORDER BY u.user_id;''', client_id) 
        select_list = cur.fetchall()
        pprint(select_list)



def delete_phone(cur, client_id, phone):
    cur.execute('''DELETE FROM phone
                   WHERE user_id = %s AND number like %s''', (client_id,phone,)) 
    conn.commit()
    print(f'Номер {phone} удален у {client_id}')


def delete_client(cur, client_id):
    cur.execute('''DELETE FROM phone
                   WHERE user_id = %s''', (client_id,)) 
    cur.execute('''DELETE FROM users
                   WHERE user_id = %s''', (client_id,))
    conn.commit()
    print(f'Клиент успешно удолен')


def find_client(cur, first_name=None, last_name=None, email=None, phone=None):

    query_list = ''
    tuple_keys = ()


    if first_name != None:
        query_list = 'WHERE u.first_name LIKE %s'
        tuple_keys += (first_name, )

    if last_name != None:
        query_list += 'WHERE u.last_name LIKE %s' if query_list == '' else ' and u.last_name LIKE %s'
        tuple_keys += (last_name, )

    if email != None:
        query_list += 'WHERE u.email LIKE %s' if query_list == '' else ' and u.email LIKE %s'
        tuple_keys += (email, )

    if phone != None:
        query_list += 'WHERE p.number LIKE %s' if query_list == '' else ' and p.number LIKE %s'
        tuple_keys += (phone, )

    
    cur.execute( '''SELECT u.user_id, u.first_name, u.last_name, u.email, p.number FROM users u
                    LEFT JOIN phone p ON u.user_id = p.user_id 
                    '''+query_list+'''
                    ORDER BY u.user_id;''', tuple_keys) 

    
    select_list = cur.fetchall()
    pprint(select_list)
    
    

conn = psycopg2.connect(database="HW_crud_from_python", user="postgres", password="1234", host="localhost", port=5432)


with conn.cursor() as cur:
    
    pass

conn.close()