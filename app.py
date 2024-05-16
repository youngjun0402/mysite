# flask 프레임 워크 안에 특정 기능들을 로드
from flask import Flask, render_template, request, redirect, url_for, session
# mysql과 연동을 하는 라이브러리 로드
import pymysql
from datetime import timedelta

# Flask라는 Class 생성
app = Flask(__name__)
# secret_key 설정(session데이터 암호화 키)
app.secret_key = 'ABC'
# session의 지속시간을 설정
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=10)
# 세션 데이터 초기화
# session.clear()
# DB server와 연결하고 -> 가상공간 Cursor 생성 -> 
# 매개변수 query문, data 값을 이용하여 질의를 보내고->
# 결과 값을 받아오거나 DB server에 동기화 -> DB server와의 연결을 좋료
def db_execute(query, *data):
    # 데이터베이스와 연결
    _db = pymysql.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        password = '1234',
        db = 'ubion'
    )
    # 가상공간 Cursor 생성
    cursor = _db.cursor(pymysql.cursors.DictCursor)
    # 매개변수 query, data를 이용하여 질의
    cursor.execute(query, data)
    # query가 select라면 결과값을 변수(result)에 저장
    if query.strip().lower().startswith('select'):
        result = cursor.fetchall()
    # query가 select가 아니라면 DB server와 동기화하고
    # 변수(result)는 Query OK 문자를 대입
    else:
        _db.commit()
        result = 'Query OK'
    # 데이터베이스 서버와의 연결을 종료
    _db.close()
    # 결과(result)를 되돌려 준다.
    return result 

# 메인페이지 api 생성
# 로그인 화면
@app.route("/")
def index():
    # 세션에 데이터가 존재한다면?
    if 'user_id' in session:
        return redirect('/index')
    else:
        # 요청이 들어왔을때 state라는 데이터가 존재하면
        try:
        # 로그인이 실패한 경우
            _state = request.args['state']
        except:
        # 처음 로그인 화면을 로드한 경우
            _state = 1
    # login.html 되돌려준다.
    return render_template('login.html', state = _state)

# 로그인 화면에서 id, passward 데이터를 보내는 api 생성
@app.route("/main", methods=['post'])
def main():
    # 유저가 보낸 데이터 : id, password
    # 유저가 보낸 id값의 key -> input_id
    # 유저가 보낸 password값의 key -> input_pass
    _id = request.form['input_id']
    _pass = request.form['input_pass']
    # 받아온 데이터를 확인
    print(f"/main[post] -> 유저 id : {_id}, password : {_pass}")
    # 유저가 보낸 데이터를 DB server에 table data와 비교
    login_query = """
        select
        *
        from
        user
        where
        id = %s
        and
        password = %s
    """
    # 함수를 호출
    db_result = db_execute(login_query, _id, _pass)
    # 로그인의 성공 여부 (조건식?? db_result가 존재하는가?)
    if db_result:
        # 로그인이 성공하는 경우 -> main.html을 되돌려준다.
        # session에 데이터를 저장(dict에 새로운 키:벨류 추가)
        session['user_id'] = _id
        session['user_pass'] = _pass
        return redirect('/index')
        # return "login ok"
    else:
        # 로그인이 실패하는 경우 -> 로그인 화면('/')으로 되돌아간다
        return redirect('/?state=2')
        # return "login fail"
# /index 주소 api 생성
@app.route('/index')
def index2():
    # 세션에 데이터가 존재한다면 main.html로 되돌려준다.
    if "user_id" in session:
        return render_template('main.html')
    # 세션에 데이터가 존재하지 않는다면 로그인화면으로 되돌아간다.
    else:
        return redirect('/')
# 회원가입 화면을 보여주는 api 생성
@app.route('/signup')
def signup():
    return render_template('signup.html')

# id 사용 유무를 판단하는 api
@app.route('/check_id', methods=['post'])
def check_id():
    # 프론트에서 비동기 통신으로 보내는 id 값을 변수에 저장
    _id = request.form['input_id']
    # 유저에게 받은 데이터 확인
    print(f"/check_id[post] -> 유저 id : {_id}")
    # 유저가 보낸 id값이 사용이 가능한가?
    # 조건? -> 해당하는 아이디로 table에 데이터가 존재하는가?
    check_id_query = """
    select * from user
    where id = %s
    """ 
    # 함수 호출
    db_result = db_execute(check_id_query, _id)
    # id가 사용가능한 경우 : db_result 존재하지 않을때
    if db_result:
        result = "0"
    else:
        result = "1"
    return result

# 회원 정보를 받아와서 데이터베이스에 삽입을 하는 api
@app.route('/signup2', methods=['post'])
def signup2():
    # 유저가 보낸 데이터를 변수에 저장
    _id = request.form['input_id']
    _pass = request.form['input_pass']
    _name = request.form['input_name']
    print(f"/signup2[post] -> 유저 ID : {_id}, password : {_pass}, name = {_name}")
    # 쿼리문 작성
    insert_user_query = """
        insert into `user`
        valuse (%s, %s, %s)
    """
    # 함수 호출 (에러가 발생하는 겨우가 있으니 try 생성)
    try:
        db_result = db_execute(insert_user_query, _id, _pass, _name)
        print(db_result)
    except:
        db_result = 3
    # 로그인 화면으로 되돌아간다.
    if db_result == 3:
        return redirect('/?state={db_result}')
    else:
        return redirect('/')
    
# 로그아웃
@app.route('/logout')
def logout():
    # 세션 데이터를 제거
    session.clear()
    return redirect('/')

# 웹 서버를 실행
app.run(debug=True)  # debug=True -> 파일이 변할때 마다 수정(개발자모드)