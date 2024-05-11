from flask import Flask, request, jsonify, Response, send_from_directory, g
import json
from flask_cors import CORS
import mysql.connector
import logging
import os
import uuid
from datetime import datetime
from mysql.connector import errorcode
from dotenv import load_dotenv
load_dotenv()
import requests

app = Flask(__name__)
CORS(
    app
)

file_name_input_plt = '/backend/input.plt'
word_container_url = 'http://word:5001/generate-docx'
static_folder = "backend/files"
# file_name_input_plt = 'input.plt'
# word_container_url = 'http://localhost:7007/generate-docx'
# static_folder = "files"
static_url_path='/files'
dir_to_frontend = "http://localhost:5000/files/"
connection = None

HOST = os.getenv("MYSQL_HOST")
PORT = os.getenv("MYSQL_PORT")
PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

# HOST="127.0.0.1"
# PORT=3307

DATABASE="ai"
TABLE_WAITING_STATUSES = "waiting_statuses"
TABLE_AI_TYPES = "ai_types"
TABLE_TEMPLATES = "templates"
TABLE_DOCUMENTS = "documents"
TABLE_DOCUMENT_TEXTS = "document_texts"

WAITING_STATUSES_PROCESS_PENDING = 0
WAITING_STATUSES_PROCESS_IN_PROGRESS = 1
WAITING_STATUSES_PROCESS_COMPLETED = 9
WAITING_STATUSES_FRONTEND_ERROR = 51
WAITING_STATUSES_BACKEND_ERROR = 52
WAITING_STATUSES_LLM_ERROR = 53
WAITING_STATUSES_TIMEOUTERROR = 80
WAITING_STATUSES_CANCEL_ERROR = 90

#logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",filename="/logs/backend_logs.log")
#logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s:%(name)s - %(message)s",filename="backend.log")

def query_database_error(err):
    """
    Handle errors that occur during DATABASE queries.

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
    Handle errors that occur during DATABASE connection.

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
        USER (str): The username for connecting to the DATABASE.
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
            print(f"再試行します...")
            logging.warning(f"再試行します...")
            continue

@app.before_request
def initialize():
    """
    Initialize database connection before handling request.
    """
    logging.info(">initialize():")
    try:
        g.connection = connect_to_database(HOST, DATABASE, PASSWORD, PORT)
        if g.connection.is_connected():
            return
    except Exception as e:
        connect_database_error(e)
        return

@app.teardown_request
def close_connection(exception):
    """
    Close database connection after handling request.
    """
    logging.info(">close_connection():")
    connection = getattr(g, 'connection', None)
    if connection is not None:
        connection.close()

#新規にdocumentを発行する
@app.route('/api/jsc/documents', methods=['POST'])
def generate_document_id():
    """
    Generate a unique document ID.

    Args:
        None

    Returns:
        json: A JSON response containing the generated document ID.
    """
    logging.info(">generate_document_id():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO {} (document_id) VALUES (NULL)".format(TABLE_DOCUMENTS))
        connection.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        document_id = cursor.fetchone()[0]
        cursor.close()
        logging.info(">generate_document_id()の戻り値: %s", document_id)
        return jsonify({"document_id": document_id}), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#ドキュメントにノード処理情報を追加する
@app.route('/api/jsc/documents/<int:document_id>/texts', methods=['POST'])
def generate_document_text_id(document_id):
    """
    Generate a unique document text ID for a given document.

    Args:
        document_id (int): The ID of the document for which to generate the text ID.

    Returns:
        json: A JSON response containing the generated document text ID.
    """
    logging.info(">generate_document_text_id():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        data = request.json
        user_format = data.get('user_format', '')
        user_case_memo = data.get('user_case_memo', '')
        sample_case_memo = data.get('sample_case_memo', '')
        sample_format = data.get('sample_format', '')
        sample_generated_text = data.get('sample_generated_text', '')
        ai_type_id = data.get('ai_type_id', '')
        cursor.execute("""
            SELECT MAX(document_text_id) FROM {}
        """.format(TABLE_DOCUMENT_TEXTS))
        max_document_text_id_temp = cursor.fetchone()[0]
        max_document_text_id = max_document_text_id_temp + 1 if max_document_text_id_temp is not None else 1
        cursor.execute("""
    INSERT INTO `document_texts` (
        `document_text_id`,
        `document_id`,
        `waiting_status_id`,
        `ai_type_id`,
        `sample_case_memo`,
        `sample_format`,
        `sample_generated_text`,
        `user_case_memo`,
        `user_format`,
        `user_generated_text`,
        `ai_generate_start_datetime`,
        `ai_generate_end_datetime`,
        `created_datetime`,
        `updated_datetime`
    ) VALUES (
         %s, %s, '0', %s, %s, %s, %s, %s, %s, NULL, NULL, NULL, NULL, NULL
    )
""", (max_document_text_id, document_id, ai_type_id, sample_case_memo, sample_format, sample_generated_text, user_case_memo, user_format))
        connection.commit()
        cursor.execute("""
            SELECT COUNT(*) FROM {}
            WHERE waiting_status_id = 0
        """.format(TABLE_DOCUMENT_TEXTS))
        queue_count_total = cursor.fetchone()[0]
        cursor.close()
        response_data = {
            "document_text_id": max_document_text_id,
            "waiting_status_id": WAITING_STATUSES_PROCESS_PENDING,
            "queue_count_total": queue_count_total
        }
        logging.info(">generate_document_text_id()の戻り値: %s", response_data)
        return jsonify(response_data), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        if err.errno == errorcode.ER_BAD_FIELD_ERROR:
            return jsonify({"message": f"Invalid parameters: {str(err)}"}), 400
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            return jsonify({"message": f"Record not found: {str(err)}"}), 404
        else:
            return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#テンプレート一覧の取得
@app.route('/api/jsc/templates', methods=['GET'])
def get_templates_list():
    logging.info(">get_templates():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute("SELECT template_id, name FROM templates")
        result = cursor.fetchall()
        cursor.close()
        templates_list = []
        for temp in result:
            template_id = temp[0]
            name = temp[1]
            template = {"template_id": template_id, "name": name}
            templates_list.append(template)
        logging.info(">get_templates()の戻り値: %s", templates_list)
        return jsonify(templates_list), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

def add_user_format(node):
    node["user_format"] = node["sample_format"]
    if "children" in node and node["children"]:
        for child in node["children"]:
            add_user_format(child)

#テンプレート詳細の取得
@app.route('/api/jsc/templates/<int:template_id>', methods=['GET'])
def get_templates_content(template_id):
    logging.info(">get_templates_content():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute("SELECT template_id, name, sample_case_memo, template_tree FROM templates where template_id = %s", (template_id,))
        result = cursor.fetchall()
        cursor.close()
        templates_list = []
        for temp in result:
            template_id = temp[0]
            name = temp[1]
            sample_case_memo = temp[2]
            template_tree_str = temp[3]
            template_tree = json.loads(template_tree_str)
            template_tree = json.loads(template_tree_str)
            for node in template_tree:
                add_user_format(node)  # add user_format
            template = {"template_id": template_id, "name": name, "sample_case_memo": sample_case_memo, "template_tree": template_tree}
            templates_list.append(template)
        for template in templates_list:
            template["user_case_memo"] = template["sample_case_memo"]
        logging.info(">get_templates_content()の戻り値: %s", templates_list)
        return jsonify(templates_list), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        if err.errno == errorcode.ER_BAD_FIELD_ERROR:
            return jsonify({"message": f"Invalid parameters: {str(err)}"}), 400
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            return jsonify({"message": f"Record not found: {str(err)}"}), 404
        else:
            return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#複数のノードのステータスを一括取得
@app.route('/api/jsc/documents/<document_id>/texts', methods=['GET'])
def get_node_id_status(document_id):
    logging.info(">get_node_ids():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM {}
            WHERE waiting_status_id = 0 AND document_id <= %s
        """.format(TABLE_DOCUMENT_TEXTS), (document_id,))
        queue_count_current = cursor.fetchone()[0]
        data = request.json
        results = []
        if data['document_text_ids']:
            for node_id in data['document_text_ids']:
                cursor.execute(f"SELECT document_text_id, waiting_status_id FROM document_texts WHERE document_text_id = {node_id}")
                result = cursor.fetchone()
                if result:
                    result_dict = {
                        "document_text_id": result[0],
                        "waiting_status_id": result[1]
                    }
                    results.append(result_dict)
        else:
            cursor.execute(f"SELECT document_text_id, waiting_status_id FROM document_texts WHERE document_id = {document_id}")
            result = cursor.fetchall()
            for row in result:
                result_dict = {
                    "document_text_id": row[0],
                    "waiting_status_id": row[1]
                }
                results.append(result_dict)
        cursor.close()
        response_data = {
            "queue_count_current": queue_count_current,
            "document_texts_status": results
        }
        logging.info(">get_node_id_status()の戻り値: %s", response_data)
        return jsonify(response_data), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        if err.errno == errorcode.ER_BAD_FIELD_ERROR:
            return jsonify({"message": f"Invalid parameters: {str(err)}"}), 400
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            return jsonify({"message": f"Record not found: {str(err)}"}), 404
        else:
            return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#documentに紐づくノードの処理待ちのものをすべてキャンセル
@app.route('/api/jsc/documents/<document_id>/texts', methods=['DELETE'])
def cancel_document_id(document_id):
    logging.info(">cancel_document_id():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE {}
        SET waiting_status_id = 90
        WHERE document_id = %s
        """.format(TABLE_DOCUMENT_TEXTS), (document_id,))
        connection.commit()
        logging.info(">cancel_document_id()の戻り値無し")
        return '', 200
    except mysql.connector.Error as err:
        query_database_error(err)
        if err.errno == errorcode.ER_BAD_FIELD_ERROR:
            return jsonify({"message": f"Invalid parameters: {str(err)}"}), 400
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            return jsonify({"message": f"Record not found: {str(err)}"}), 404
        else:
            return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#ノードの詳細情報の取得
@app.route('/api/jsc/documents/<document_id>/texts/<document_text_id>', methods=['GET'])
def get_node_content(document_id, document_text_id):
    logging.info(">get_node_content():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT waiting_status_id, ai_type_id, user_generated_text, "
            f"ai_generate_start_datetime, ai_generate_end_datetime "
            f"FROM document_texts "
            f"WHERE document_id = %s AND document_text_id = %s",
            (document_id, document_text_id)
        )
        result = cursor.fetchone()
        if result:
            waiting_status_id = result[0]
            ai_type_id = result[1]
            user_generated_text = result[2]
            ai_generate_start_datetime = result[3]
            ai_generate_end_datetime = result[4]
            cursor.close()
            response_data = {
                "waiting_status_id": waiting_status_id,
                "ai_type_id": ai_type_id,
                "ai_generated_text": user_generated_text,
                "ai_generate_start_datetime": ai_generate_start_datetime,
                "ai_generate_end_datetime": ai_generate_end_datetime
            }
            logging.info(">get_node_content()の戻り値: %s", response_data)
            return jsonify(response_data), 200
        else:
            cursor.close()
            return jsonify({"message": "No data found"}), 404
    except mysql.connector.Error as err:
        query_database_error(err)
        if err.errno == errorcode.ER_BAD_FIELD_ERROR:
            return jsonify({"message": f"Invalid parameters: {str(err)}"}), 400
        elif err.errno == errorcode.ER_NO_SUCH_TABLE:
            return jsonify({"message": f"Record not found: {str(err)}"}), 404
        else:
            return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#ai_types一覧の取得
@app.route('/api/jsc/ai_types', methods=['GET'])
def get_ai_types():
    logging.info(">get_ai_types():")
    cursor = None
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT ai_type_id, name, attention_text "
            f"FROM ai_types"
        )
        result = cursor.fetchall()
        cursor.close()
        ai_types_list = []
        for temp in result:
            ai_type_id = temp[0]
            name = temp[1]
            attention_text = temp[2]
            template = {"ai_type_id": ai_type_id, "name": name, "attention_text": attention_text}
            ai_types_list.append(template)
        logging.info(">get_ai_types()の戻り値: %s", ai_types_list)
        return jsonify(ai_types_list), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

#wating_statuses一覧の取得
@app.route('/api/jsc/waiting_statuses', methods=['GET'])
def get_wating_statuses():
    logging.info(">get_wating_statuses():")
    try:
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT waiting_status_id, name "
            f"FROM waiting_statuses"
        )
        result = cursor.fetchall()
        cursor.close()
        ai_types_list = []
        for temp in result:
            waiting_status_id = temp[0]
            name = temp[1]
            template = {"waiting_status_id": waiting_status_id, "name": name}
            ai_types_list.append(template)
        logging.info(">get_wating_statuses()の戻り値: %s", ai_types_list)
        return jsonify(ai_types_list), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

# 木構造を再帰的に処理し、"*"で階層を設定
def traverse_tree(node, depth, result):
    logging.info(">traverse_tree():")
    result.append("*" * depth + node["node_name"])
    if node["user_generated_text"]:
        user_text_lines = node["user_generated_text"].split("\n")
        result.append("*" * (depth + 1) + user_text_lines[0])
        for line in user_text_lines[1:]:
            result.append("*" * (depth + 1) + line)
    for child in node["children"]:
        traverse_tree(child, depth + 1, result)

# 全体の木構造を処理
def process_tree(tree):
    logging.info(">process_tree():")
    result = []
    for node in tree:
        traverse_tree(node, 1, result)
    logging.info(">process_tree()の戻り値: %s", result)
    return "\n".join(result)

# 静的ファイルを提供するエンドポイントを定義
@app.route('/files/<path:filename>')
def serve_static(filename):
    logging.info(">serve_static():")
    try:
        return send_from_directory('files', filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# frontendで送信られた内容で、documentsテーブルgenerated_content列をデータベースへの書き込みとinput.pltを作成し、input.pltをwordファイルを生成コンテナに送信し、リスポンス取得と格納し、ファイルdownload為のURLと生成時間をfrontendに返す。
@app.route('/api/jsc/documents/<document_id>/export', methods=['PUT'])
def export_word(document_id):
    logging.info(">export_word():")
    try:
        # frontendで送信られた内容でinput.pltを作成
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        result = process_tree(data["user_generated_content_tree"])
        if not result:
            return jsonify({"error": "No user generated content tree provided"}), 400
        try:
            with open("input.plt", "w") as f: #★★★
                f.write(result)
        except Exception as e:
            return jsonify({"error": "Failed to write to file: {}".format(str(e))}), 500
        # documentsテーブルgenerated_content列をデータベースへの書き込み
        user_generated_content_tree = data["user_generated_content_tree"]
        generated_content_json = json.dumps(user_generated_content_tree)
        connection = getattr(g, 'connection', None)
        cursor = connection.cursor()
        update_query = """
        UPDATE documents
        SET generated_content = %s
        WHERE document_id = %s
        """
        cursor.execute(update_query, (generated_content_json, document_id))
        connection.commit()
        # input.pltをwordファイルを生成コンテナに送信し、リスポンス取得と格納
        parent_directory = os.path.dirname(os.getcwd())
        file_path = os.path.join(parent_directory, file_name_input_plt)
        unique_id = str(uuid.uuid4())
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # 推測されないように、安全な乱数ファイル名作成
        file_name_upload = f"{current_datetime}_{unique_id}.docx"
        response = requests.post(word_container_url, headers={'Content-Type': 'text/plain'}, data=open(file_path, 'rb'))
        if response.status_code != 200:
            return jsonify({"error": "Failed to generate Word document"}), 500
        try:
            files_directory = os.path.join(parent_directory, static_folder)
            file_path = os.path.join(files_directory, file_name_upload)
            with open(file_path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            return jsonify({"error": "Failed to write to file: {}".format(str(e))}), 500
        # ファイルdownload為のURLと生成時間
        exported_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_url = dir_to_frontend + file_name_upload
        response_data = {
        "exported_datetime": exported_datetime,
        "result": result_url
        }
        logging.info(">export_word()の戻り値: %s", response_data)
        return jsonify(response_data), 200
    except mysql.connector.Error as err:
        query_database_error(err)
        return jsonify({"message": f"Error occurred: {str(err)}"}), err.errno

if __name__ == '__main__':
    app.run()
