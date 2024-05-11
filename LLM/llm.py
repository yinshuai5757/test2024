import mysql.connector
from datetime import datetime
import openai
import asyncio
import logging
import os
import requests
from mysql.connector import errorcode
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

openai.api_type = os.getenv("openai_api_type")
openai.api_version = os.getenv("openai_api_version")
openai.api_base = os.getenv("openai_api_base")
openai.api_key = os.getenv("openai_api_key")
engine = os.getenv("engine")

HOST = os.getenv("MYSQL_HOST")
PORT = os.getenv("MYSQL_PORT")
PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
DATABASE="ai"
TABLE_NAME = "document_texts"

WAITING_STATUSES_PROCESS_PENDING = 0
WAITING_STATUSES_PROCESS_IN_PROGRESS = 1
WAITING_STATUSES_PROCESS_COMPLETED = 9
WAITING_STATUSES_FRONTEND_ERROR = 51
WAITING_STATUSES_BACKEND_ERROR = 52
WAITING_STATUSES_LLM_ERROR = 53
WAITING_STATUSES_TIMEOUTERROR = 80
WAITING_STATUSES_CANCEL_ERROR = 90
AI_TYPES_INTERNAL_AI = 1
AI_TYPES_EXTERNAL_AI = 2
QUEUE_MAX_SIZE = 2
CYCLE_TIME = 1

# HOST="127.0.0.1"
# PORT=3307

global_llm_queue = asyncio.Queue(QUEUE_MAX_SIZE)
local_llm_queue = asyncio.Queue(1)
lock = asyncio.Lock()

# logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",filename="/logs/my_llm_logs.log")
# logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",filename="llm.log")

def query_database_error(err):
    """
    Display corresponding error messages based on the returned error codes during DATABASE QUERY.

    Args:
        err: The error object representing the DATABASE error.

    Raises:
        None

    Returns:
        None
    """
    logging.info(">query_database_error():")
    if err.errno == errorcode.ER_PARSE_ERROR:
        print("MYSQLクエリエラー: クエリの構文解析中にエラーが発生しました。")
        logging.error("MYSQLクエリエラー: クエリの構文解析中にエラーが発生しました。")
    elif err.errno == errorcode.ER_NO_SUCH_TABLE:
        print("MYSQLクエリエラー: 指定されたテーブルが存在しません。")
        logging.error("MYSQLクエリエラー: 指定されたテーブルが存在しません。")
    elif err.errno == errorcode.ER_DUP_ENTRY:
        print("MYSQLクエリエラー: 一意制約に違反する重複エントリが挿入されました。")
        logging.error("MYSQLクエリエラー: 一意制約に違反する重複エントリが挿入されました。")
    elif err.errno == errorcode.ER_LOCK_WAIT_TIMEOUT:
        print("MYSQLクエリエラー: ロック待ちタイムアウトが発生しました。")
        logging.error("MYSQLクエリエラー: ロック待ちタイムアウトが発生しました。")
    elif err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
        print("MYSQLクエリエラー: テーブルがすでに存在します。")
        logging.error("MYSQLクエリエラー: テーブルがすでに存在します。")
    elif err.errno == errorcode.ER_DATA_TOO_LONG:
        print("MYSQLクエリエラー: データが列の長さを超えました。")
        logging.error("MYSQLクエリエラー: データが列の長さを超えました。")
    elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("MYSQLクエリエラー: クエリの実行権限がありません。")
        logging.error("MYSQLクエリエラー: クエリの実行権限がありません。")
    elif err.errno == errorcode.ER_TABLEACCESS_DENIED_ERROR:
        print("MYSQLクエリエラー: テーブルへのアクセス権がありません。")
        logging.error("MYSQLクエリエラー: テーブルへのアクセス権がありません。")
    else:
        print("MYSQLクエリエラー:", err)
        logging.error("MYSQLクエリエラー:", err)
        print("エラーコード:", err.errno)
        logging.error("エラーコード:", err.errno)

def connect_database_error(err):
    """
    Display corresponding error messages based on the returned error codes during DATABASE connection.

    Args:
        err: The error object representing the DATABASE connection error.

    Raises:
        None

    Returns:
        None
    """
    logging.info(">connect_database_error():")
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("ユーザーがアクセス権を持っていない。")
        logging.error("ユーザーがアクセス権を持っていない。")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("MYSQL接続エラー: データベースが存在しません。")
        logging.error("MYSQL接続エラー: データベースが存在しません。")
    elif err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
        print("MYSQL接続エラー: データベースにアクセスする権限がない")
        logging.error("MYSQL接続エラー: データベースにアクセスする権限がない")
    elif err.errno == errorcode.ER_HOST_IS_BLOCKED:
        print("MYSQL接続エラー: 接続を試みたホストが MySQL サーバーによってブロックされている")
        logging.error("MYSQL接続エラー: 接続を試みたホストが MySQL サーバーによってブロックされている")
    elif err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
        print("MYSQL接続エラー: データベースへのアクセスが拒否された。")
        logging.error("MYSQL接続エラー: データベースへのアクセスが拒否された。")
    else:
        print("MYSQL接続エラー:", err)
        logging.error("MYSQL接続エラー:", err)
        print("エラーコード:", err.errno)
        logging.error("エラーコード:", err.errno)

def connect_to_database(HOST, DATABASE, PASSWORD, PORT):
    """Connects to a MySQL DATABASE.

    Logs the entry of the function using logging.info.
    Enters an infinite loop to ensure retrying in case of connection failure.
    Attempts to establish a connection to the MySQL DATABASE using the mysql.connector.connect method.
    If the connection is successful, it returns the connection object and exits the function.
    If the connection fails, catches the mysql.connector.Error exception, executes the connect_database_error function passing the exception object, then prints "Retrying..." message to the console and logs the same warning message.
    Continues to the next iteration of the loop, retrying the connection until success or reaching the maximum retry count.

    Args:
        HOST (str): The hostname or IP address of the DATABASE server.
        DATABASE (str): The name of the DATABASE to connect to.
        PASSWORD (str): The PASSWORD for the DATABASE USER.
        PORT (int): The PORT number on which the DATABASE server is listening.

    Raises:
        None

    Returns:
        connection: The connection object upon successful connection to the DATABASE.
    """
    logging.info(">connect_to_database():")
    while True:
        try:
            connection = mysql.connector.connect(
                host=HOST,
                database=DATABASE,
                user='root',
                password=PASSWORD,
                port=PORT
            )
            return connection
        except mysql.connector.Error as err:
            connect_database_error(err)
            # print("データベース接続失敗の為、{}秒毎にデータベース接続します。".format(CYCLE_TIME))
            # logging.warning("データベース接続失敗の為、{}秒毎にデータベース接続します。".format(CYCLE_TIME))
            # await asyncio.sleep(CYCLE_TIME)
            print(f"再試行します...")
            logging.warning(f"再試行します...")
            continue

def poll_ai_database(ai_type):
    """Polls the DATABASE to get information.

    Logs the entry of the function using logging.info.
    Initializes poll_result to None.
    Establishes a DATABASE connection using the connect_to_database function.
    Checks if the connection is established successfully.
    If the connection is successful:
    Creates a cursor object with dictionary=True to fetch results as dictionaries.
    Constructs a SQL query to select document information from the DATABASE table based on the provided AI type.
    Executes the query.
    Fetches the first row of the result set.
    If a row is found (poll_result is not None), updates the waiting_status_id of the document to indicate that processing is in progress.
    Commits the transaction.
    If no row is found, prints a message to indicate the absence of pending records and logs the same.
    Closes the cursor and the DATABASE connection.
    If the connection fails, prints an error message to indicate the MySQL connection error and logs the same.
    Returns poll_result, which contains document information if found, or None if no document is found.

    Args:
        ai_type (int): The type of AI for which to poll the DATABASE.

    Raises:
        None

    Returns:
        dict or None: A dictionary containing information about the document if found, None otherwise.
    """
    logging.info(">poll_ai_database():")
    poll_result = None
    connection = connect_to_database(HOST, DATABASE, PASSWORD, PORT)
    if connection.is_connected():
        try:
            cursor = connection.cursor(dictionary=True)
            query_global = (f"SELECT document_text_id, waiting_status_id, ai_type_id, sample_case_memo, sample_format, sample_generated_text, user_case_memo, user_format "
                            f"FROM {TABLE_NAME} "
                            f"WHERE waiting_status_id = {WAITING_STATUSES_PROCESS_PENDING} AND ai_type_id = {ai_type} "
                            f"ORDER BY created_datetime ASC LIMIT 1")
            cursor.execute(query_global)
            poll_result = cursor.fetchone()
            if poll_result:
                update_query = (f"UPDATE {TABLE_NAME} SET waiting_status_id = {WAITING_STATUSES_PROCESS_IN_PROGRESS} "
                                "WHERE document_text_id = %s")
                cursor.execute(update_query, (poll_result['document_text_id'],))
                connection.commit()
                logging.info("document_text_id = %s : wait_stausが1になった",poll_result['document_text_id'])#★#★#★
            else:
                # print("処理待ちレコードが存在しません。poll_ai_database関数終了。")
                logging.info("処理待ちレコードが存在しません。poll_ai_database関数終了。")
        except mysql.connector.Error as err:
            query_database_error(err)
        finally:
            cursor.close()
            connection.close()
    else:
        print("MySQL接続エラーで、poll_ai_database関数終了。")
        logging.error("MySQL接続エラーで、poll_ai_database関数終了。")
    return poll_result

def generate_global_ai_response(sample_format, sample_case_memo, sample_generated_text, user_format, user_case_memo, thread_name):
    """Generates a response from the global AI based on input parameters.

    Logs the entry of the function using logging.info.
    Initializes ai_response to None.
    Retrieves the current datetime as ai_generate_start_datetime.
    Tries to generate a response from the global AI using OpenAI's ChatCompletion API.
    Constructs a message with the provided sample_format, sample_case_memo, user_format, and user_case_memo.
    Sends the message to the AI model for generating a response.
    If a response is received:
    Stores the response in ai_response.
    Retrieves the current datetime as ai_generate_end_datetime.
    Logs the generated response, start datetime, and end datetime.
    Returns a tuple containing ai_response, ai_generate_start_datetime, and ai_generate_end_datetime.
    If an error occurs during the process, prints an error message and logs the same.
    Returns None, None, None if no response is generated or an error occurs.

    Args:
        sample_format (str): The format of the sample data.
        sample_case_memo (str): The case memo of the sample data.
        sample_generated_text (str): The generated text of the sample data.
        user_format (str): The format provided by the USER.
        user_case_memo (str): The case memo provided by the USER.
        thread_name (str): The name of the thread executing the function.

    Returns:
        tuple: A tuple containing the AI-generated response, the start datetime of generation, and the end datetime of generation.
    """
    logging.info(f"{thread_name}>generate_global_ai_response():")
    logging.info(f"{thread_name}>generate_global_ai_response()の引数: sample_format={sample_format}, sample_case_memo={sample_case_memo}, sample_generated_text={sample_generated_text}, user_format={user_format}, user_case_memo={user_case_memo}")
    ai_response = None
    ai_generate_start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = openai.ChatCompletion.create(
            engine=engine,
            messages=[
                {"role": "system", "content": "あなたは、userが与えたFORMATの内容を変換するＡＩです。\n    変換方法は次のとおりです。\n    ①userはあなたに、FORMATを与えます。\n    ②FORMATには'[『リースに関する事務作業全般』の一般的な内容を具体的に説明]である。'のような記載があります。この場合、'['と']'で囲まれた部分はあなたへの指示です。その指示に従って、例えば「新しいリース物件の登録、紹介記事作成、受注応対、修繕対応等である。」のように、指示されたとおりの「だ・である」調の文章に変換します。\n    ③最後に、変換したFORMATのみを出力します。それ以外は出力しません。"},
                {"role": "user", "content": f"FORMAT: {sample_format}\nCASE_MEMO: {sample_case_memo}"},
                {"role": "assistant", "content": sample_generated_text},
                {"role": "user", "content": f"FORMAT: {user_format}\nCASE_MEMO: {user_case_memo}"},
            ]
        )
        if response["choices"][0]["message"]["content"]:
            ai_response = response["choices"][0]["message"]["content"]
            ai_generate_end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"{thread_name}>generate_global_ai_response()の戻り値: ai_response={ai_response}, ai_generate_start_datetime={ai_generate_start_datetime}, ai_generate_end_datetime={ai_generate_end_datetime}")
            return ai_response, ai_generate_start_datetime, ai_generate_end_datetime
        else:
            print("Failed to get response")
    except Exception as e:
        print(f"{thread_name}>Error in generate_global_ai_response(): {e}")
        logging.error(f"{thread_name}>Error in generate_global_ai_response(): {e}")
    return None, None, None

def generate_local_ai_response(sample_format, sample_case_memo, sample_generated_text, user_format, user_case_memo, thread_name):
    """Generates a response from the local AI based on input parameters.

    Logs the entry of the function using logging.info.
    Initializes ai_response to None.
    Retrieves the current datetime as ai_generate_start_datetime.
    Tries to generate a response from the local AI using the specified URI and OpenAI's ChatCompletion API.
    Constructs a message with the provided sample_format, sample_case_memo, user_format, and user_case_memo.
    Sends the message to the AI model for generating a response.
    If a response is received:
        Stores the response in ai_response.
        Retrieves the current datetime as ai_generate_end_datetime.
        Logs the generated response, start datetime, and end datetime.
        Returns a tuple containing ai_response, ai_generate_start_datetime, and ai_generate_end_datetime.
    If an error occurs during the process:
        Prints an error message and logs the same.
        Returns None, None, None if no response is generated or an error occurs.

    Args:
        sample_format (str): The format of the sample data.
        sample_case_memo (str): The case memo of the sample data.
        sample_generated_text (str): The generated text of the sample data.
        user_format (str): The format provided by the USER.
        user_case_memo (str): The case memo provided by the USER.
        thread_name (str): The name of the thread executing the function.

    Returns:
        tuple: A tuple containing the AI-generated response, the start datetime of generation, and the end datetime of generation.
    """
    logging.info(f"{thread_name}>generate_local_ai_response():")
    logging.info(f"{thread_name}>generate_local_ai_response()の引数: sample_format={sample_format}, sample_case_memo={sample_case_memo}, sample_generated_text={sample_generated_text}, user_format={user_format}, user_case_memo={user_case_memo}")
    ai_response = None
    stop = ["[", "<"]
    ai_generate_start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        URI = "http://AISERVER:7005/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "あなたは、userが与えたFORMATの内容を変換するＡＩです。\n    変換方法は次のとおりです。\n    ①userはあなたに、FORMATを与えます。\n    ②FORMATには'[『リースに関する事務作業全般』の一般的な内容を具体的に説明]である。'のような記載があります。この場合、'['と']'で囲まれた部分はあなたへの指示です。その指示に従って、例えば「新しいリース物件の登録、紹介記事作成、受注応対、修繕対応等である。」のように、指示されたとおりの「だ・である」調の文章に変換します。\n    ③最後に、変換したFORMATのみを出力します。それ以外は出力しません。"},
                {"role": "user", "content": f"FORMAT: {sample_format}\nCASE_MEMO: {sample_case_memo}"},
                {"role": "assistant", "content": sample_generated_text},
                {"role": "user", "content": f"FORMAT: {user_format}\nCASE_MEMO: {user_case_memo}"},
            ],
            "stop": stop
        }
        response = requests.post(URI, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            resp = response.json()
            ai_response = resp['choices'][0]['message']['content']
            ai_generate_end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"{thread_name}>generate_global_ai_response()の戻り値: ai_response={ai_response}, ai_generate_start_datetime={ai_generate_start_datetime}, ai_generate_end_datetime={ai_generate_end_datetime}")
            return ai_response, ai_generate_start_datetime, ai_generate_end_datetime
        else:
            print("Failed to get response")
    except Exception as e:
        print(f"{thread_name}>Error in generate_global_ai_response(): {e}")
        logging.error(f"{thread_name}>Error in generate_global_ai_response(): {e}")
    return None, None, None

def write_to_ai_database(document_text_id, user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime, thread_name, ai_type_id):
    """Writes the generated response to the AI DATABASE.

    Logs the entry of the function using logging.info.
    Retrieves a DATABASE connection using the connect_to_database function.
    Checks if the connection is successful.
    If the connection is successful:
    Initializes a cursor for DATABASE operations.
    Constructs an SQL query to update the DATABASE with the generated response.
    Executes the query with the provided parameters.
    Commits the changes to the DATABASE.
    If an error occurs during DATABASE operations, handles the error using the query_database_error function.
    Closes the cursor and the DATABASE connection.
    Prints a message and logs the completion of the function.
    If the connection fails, prints an error message and logs the same.

    Args:
        document_text_id (str): The ID of the document.
        user_generated_text (str): The text generated by the USER.
        ai_generate_start_datetime (str): The start datetime of AI generation.
        ai_generate_end_datetime (str): The end datetime of AI generation.
        thread_name (str): The name of the thread executing the function.

    Returns:
        None
    """
    logging.info(f"{thread_name}>write_to_ai_database():")
    logging.info(f"{thread_name}>write_to_ai_database()の引数: document_text_id={document_text_id}, user_generated_text={user_generated_text}, ai_generate_start_datetime={ai_generate_start_datetime}, ai_generate_end_datetime={ai_generate_end_datetime}")
    connection = connect_to_database(HOST, DATABASE, PASSWORD, PORT)
    if connection.is_connected():
        try:
            cursor = connection.cursor(dictionary=True)
            query = f"""
                    UPDATE {TABLE_NAME}
                    SET
                        user_generated_text = %s,
                        ai_generate_start_datetime = %s,
                        ai_generate_end_datetime = %s,
                        waiting_status_id = {WAITING_STATUSES_PROCESS_COMPLETED}
                    WHERE
                        document_text_id = %s AND ai_type_id = %s
                    """
            cursor.execute(query, (user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime, document_text_id, ai_type_id))
            connection.commit()
        except mysql.connector.Error as err:
            query_database_error(err)
        finally:
            cursor.close()
            connection.close()
            print(f'{thread_name}個目処理完了')
            logging.info(f'{thread_name}個目処理完了')
    else:
        print("MYSQL接続エラーで、書き込みできません。write_to_ai_database関数終了。")
        logging.error("MYSQL接続エラーで、書き込みできません。write_to_ai_database関数終了。")

async def put_main_global():
    """
    Retrieve pending data from the database for external AI and add it to the global queue.

    This function handles the retrieval of pending data from the database for external AI processing. If the global queue is full,
    the function stores the pending data temporarily and retries adding it to the queue later.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">put_main_global():")
    pending_data_global = None #　QueueFullの場合のpoll_data_external情報の格納で、こうしないと、そのままpoll_data_externalを捨てられてしまう
    while True:
        try:
            if pending_data_global != None:
                poll_data_external = pending_data_global
            else:
                poll_data_external = poll_ai_database(AI_TYPES_EXTERNAL_AI)
            if poll_data_external:
                try:
                    async with lock:
                        global_llm_queue.put_nowait(poll_data_external)
                        pending_data_global = None
                except asyncio.QueueFull:
                    #print(f"global_llm_queueがいっぱいの為、putできません。")
                    logging.warning(f"global_llm_queueがいっぱいの為、putできません。")
                    await asyncio.sleep(CYCLE_TIME)
                    pending_data_global = poll_data_external
                    continue
                    # print("put Queue size:", global_llm_queue.qsize())  #★
            else:
                # print("external処理待ちレコードがないため、{}秒毎にデータベースをポーリングします。".format(CYCLE_TIME)) #★★★
                # print("put_main_global()関数 : poll_ai_database戻り値がNULL。")
                logging.info("put_main_global()関数 : poll_ai_database戻り値がNULL。")
                await asyncio.sleep(CYCLE_TIME)
                continue
        except Exception as e:
            print(f"put_main_global()にエラーが発生しました: {e}")
            logging.error(f"put_main_global()にエラーが発生しました: {e}")
            await asyncio.sleep(CYCLE_TIME)
            continue

async def put_main_local():
    """
    Retrieve pending data from the database for internal AI and add it to the local queue.

    This function handles the retrieval of pending data from the database for internal AI processing. If the local queue is full,
    the function stores the pending data temporarily and retries adding it to the queue later.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">put_main_local():")
    pending_data_local = None #　QueueFullの場合のpoll_data_external情報の格納で、こうしないと、そのままpoll_data_externalを捨てられてしまう
    while True:
        try:
            if pending_data_local != None:
                poll_data_internal = pending_data_local
            else:
                poll_data_internal = poll_ai_database(AI_TYPES_INTERNAL_AI)
            if poll_data_internal:
                try:
                    async with lock:
                        local_llm_queue.put_nowait(poll_data_internal)
                        pending_data_local = None
                except asyncio.QueueFull:
                    # print(f"global_llm_queueがいっぱいの為、putできません。")
                    # logging.warning(f"local_llm_queueがいっぱいの為、putできません。")#★★★
                    await asyncio.sleep(CYCLE_TIME)
                    pending_data_local = poll_data_internal
                    continue
                    # print("put Queue size:", local_llm_queue.qsize())  #★
            else:
                # print("internal処理待ちレコードがないため、{}秒毎にデータベースをポーリングします。".format(CYCLE_TIME))#★★★
                # print("put_main_local()関数 : poll_ai_database戻り値がNULL。")
                logging.info("put_main_local()関数 : poll_ai_database戻り値がNULL。")
                await asyncio.sleep(CYCLE_TIME)
                continue
        except Exception as e:
            print(f"put_main_local()にエラーが発生しました: {e}")
            logging.error(f"put_main_local()にエラーが発生しました: {e}")
            await asyncio.sleep(CYCLE_TIME)
            continue

async def get_poll_data_from_queue_global(name):
    """
    Process polling data retrieved from the global queue.

    This function retrieves data from the global queue for processing. It handles scenarios where the queue is empty
    by waiting for a specified time before retrying.

    Args:
        name (str): The name of the data processing.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">get_poll_data_from_queue_global():")
    while True:
        try:
            async with lock:
                element = global_llm_queue.get_nowait()
        except asyncio.QueueEmpty:
            # logging.warning(f"global_llm_queueが空の為、getできません。")#★★★
            await asyncio.sleep(CYCLE_TIME)
            continue
        # print("get Queue size:", global_llm_queue.qsize())  #★
        keys = list(element.keys())
        sample_format = element[keys[4]]
        sample_case_memo = element[keys[3]]
        sample_generated_text = element[keys[5]]
        user_format = element[keys[7]]
        user_case_memo = element[keys[6]]
        document_text_id = element[keys[0]]
        ai_type_id = element[keys[2]] #★★★
        user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime = generate_global_ai_response(sample_format, sample_case_memo, sample_generated_text, user_format, user_case_memo, name)
        if user_generated_text and ai_generate_start_datetime and ai_generate_end_datetime:
            write_to_ai_database(document_text_id, user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime, name, ai_type_id)
            await asyncio.sleep(CYCLE_TIME)
            continue
        else:
            print("write_to_ai_databaseがNULL。")
            logging.warning("generate_global_ai_response戻り値がNULL。")
            await asyncio.sleep(CYCLE_TIME)
            continue

async def get_poll_data_from_queue_local(name):
    """
    Process polling data retrieved from the local queue.

    This function retrieves data from the local queue for processing. It handles scenarios where the queue is empty
    by waiting for a specified time before retrying.

    Args:
        name (str): The name of the data processing.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">get_poll_data_from_queue_local():")
    while True:
        try:
            async with lock:
                element = local_llm_queue.get_nowait()
        except asyncio.QueueEmpty:
            # logging.warning(f"local_llm_queueが空の為、getできません。")
            await asyncio.sleep(CYCLE_TIME)
            continue
        # print("get Queue size:", local_llm_queue.qsize())  #★
        keys = list(element.keys())
        sample_format = element[keys[4]]
        sample_case_memo = element[keys[3]]
        sample_generated_text = element[keys[5]]
        user_format = element[keys[7]]
        user_case_memo = element[keys[6]]
        document_text_id = element[keys[0]]
        ai_type_id = element[keys[2]] #★★★
        user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime = generate_local_ai_response(sample_format, sample_case_memo, sample_generated_text, user_format, user_case_memo, name)
        if user_generated_text and ai_generate_start_datetime and ai_generate_end_datetime:
            write_to_ai_database(document_text_id, user_generated_text, ai_generate_start_datetime, ai_generate_end_datetime, name, ai_type_id)
            await asyncio.sleep(CYCLE_TIME)
            continue
        else:
            print("write_to_ai_databaseがNULL。")
            logging.warning("generate_global_ai_response戻り値がNULL。")
            await asyncio.sleep(CYCLE_TIME)
            continue

async def get_main():
    """
    Retrieve polling data from global and local queues.

    This function creates tasks to retrieve polling data from both global and local queues.
    It creates tasks for each queue thread and gathers them using asyncio.gather to concurrently
    retrieve data from both queues.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">get_main():")
    tasks = []
    try:
        for i in range(QUEUE_MAX_SIZE):
            task_global = asyncio.create_task(get_poll_data_from_queue_global(f'global_thr-{i}'))
            task_local = asyncio.create_task(get_poll_data_from_queue_local(f'local_thr-{i}'))
            tasks.append(task_global)
            tasks.append(task_local)
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"An error occurred in get_main: {e}")
        logging.error(f"An error occurred in get_main: {e}")

async def main():
    """
    The main asynchronous function. Executes the main processing for both global and local.

    This function gathers the execution of three main asynchronous functions:
    - put_main_global: Executes the main processing for the global aspect.
    - put_main_local: Executes the main processing for the local aspect.
    - get_main: Retrieves polling data from both global and local queues.

    Returns:
        None: This function does not return any value.
    """
    logging.info(">main():")
    try:
        await asyncio.gather(put_main_global(), put_main_local(), get_main())
    except Exception as e:
        print(f"エラー発生: {e}")
        logging.error(f"エラー発生: {e}")

if __name__ == "__main__":
    asyncio.run(main())
