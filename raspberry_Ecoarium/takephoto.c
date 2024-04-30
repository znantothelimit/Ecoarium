#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// 전역변수 선언
char pi_img_dir[] = "/home/pi/kcydir/img"; // 라즈베리파이 이미지 저장위치
char pc_ip_address[] = "192.168.94.79";
char pc_username[] = "lavie";
char pc_dst[] = "C:/vscode_kcy";

int main()
{
    for (int i = 0; i < 10; i++)
    {

        // 현재 시간 정보 가져오기
        time_t rawtime;
        struct tm *timeinfo;
        char timestamp[80];

        time(&rawtime);
        timeinfo = localtime(&rawtime);

        strftime(timestamp, sizeof(timestamp), "image-%d%H%M%S", timeinfo); // 시간 포맷 지정

        // 카메라로 사진 찍기
        char capture_command[200];
        sprintf(capture_command, "libcamera-still -o %s/%s.jpg --shutter 2222", pi_img_dir, timestamp);

        // libcamera-still 명령어 대신에 capture_command 사용
        int result = system(capture_command);
    }

    return 0;
}
