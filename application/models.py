import sqlite3
import pandas as pd



def create_tables():
    
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()

    df_table = '''
        CREATE TABLE IF NOT EXISTS df_table (
            geo_plz INTEGER,
            totalRent REAL
        );
    '''
    cursor.execute(df_table)

   
    shape_table = '''
        CREATE TABLE IF NOT EXISTS shape_table (
            plz INTEGER,
            note TEXT,
            geometry TEXT
        );
    '''
    cursor.execute(shape_table)

    conn.commit()
    conn.close()

create_tables()
print('Tables created sucessfully')



df1=pd.read_csv('/home/ashik/Downloads/datasets/immo_data.csv')
data=df1[['geo_plz','totalRent']][:190000]

shape_data=pd.read_csv('/home/ashik/luminar_python/DS/projects_main/shape_file.csv')
shape_data=shape_data[:6900]


def insert_dataframe_into_df_table(data, df_table):
    
    conn = sqlite3.connect('database.sqlite3')

    data.to_sql(df_table, conn, if_exists='replace', index=False)

    conn.close()


def insert_dataframe_into_shape_table(shape_data, shape_table):
    
    conn = sqlite3.connect('database.sqlite3')

    shape_data.to_sql(shape_table, conn, if_exists='replace', index=False)

    conn.close()


insert_dataframe_into_df_table(data,'df_table')
insert_dataframe_into_shape_table(shape_data,'shape_table')

print('Data inserted sucessfully')

