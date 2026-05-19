
# common role
서버 초기 ssh연결 및 보안설정을 자동화하는 role입니다.  
메니지드 서버에 다음과 같이 최초 1회 실행합니다.  
```
1.계정생성  
2.sudoers.d 등록  
3.컨트롤노드 ssh 공개키 등록  
4.ssh로그인 활성화, 비밀번호 로그인 비활성화  
```
# 사용법
##필요 도구
```
dnf install sshpass -y
```

##명령어
```
ansible-playbook site.yml --ask-pass -t common 
```
최초 ssh 연결 시 메니지드 노드의 비밀번호를 묻습니다. (--ask-pass)  

# 사전 조건
컨트롤 노드의 공개키 발행  
메니지드 노드 ssh 접속 가능 여부 확인  