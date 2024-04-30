#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// 전역변수 선언
char pi_img_dir[] = "/home/pi/dir/img"; // 라즈베리파이 이미지 저장위치
char pc_ip_address[] = "192.168.94.79";
char pc_username[] = "lavie";
char pc_dst[] = "C:/vscode_kcy";

int main()
{
    while (1)
    {
        fprintf(stdout, "\nEnter any key to take picture\n");
        getchar();

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

        // 사진이 성공적으로 촬영되었는지 확인
        if (result != 0)
        {
            fprintf(stderr, "Error: Failed to capture image\n");
            continue; // 사진 촬영에 실패하면 반복문의 다음 반복으로 넘어감
        }

        // SCP를 사용하여 PC로 사진 전송
        char scp_command[1000];
        char file_src[200];

        sprintf(file_src, "%s/%s.jpg", pi_img_dir, timestamp); // 시간이 포함된 파일명

        // SCP 명령 구성
        sprintf(scp_command, "scp %s %s@%s:%s", file_src, pc_username, pc_ip_address, pc_dst);

        // SCP 명령 실행
        result = system(scp_command);

        // 전송이 성공적으로 완료되었는지 확인
        if (result != 0)
        {
            fprintf(stderr, "Error: Failed to transfer image\n");
            // 추가적인 오류 처리를 수행하거나 반복문의 다음 반복으로 넘어갈 수 있음
        }
    }

    return 0;
}
