package com.example.ecoariumapp.activities

import SharedPrefManager
import android.content.Intent
import android.os.Bundle
import android.text.method.PasswordTransformationMethod
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.ImageButton
import androidx.appcompat.app.AppCompatActivity
import com.example.ecoariumapp.R
import com.example.ecoariumapp.sendRequests.sendLoginRequest

class LoginActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        // UI 요소 참조
        val loginButton: Button = findViewById(R.id.loginButton)
        val registerButton: Button = findViewById(R.id.registerButton)

        val usernameEditText: EditText = findViewById(R.id.usernameEditText)
        val passwordEditText: EditText = findViewById(R.id.passwordEditText)
        val showPasswordButton: ImageButton = findViewById(R.id.showPasswordButton)
        val keepLoginCheckBox: CheckBox = findViewById(R.id.keepLoginCheckBox)

        showPasswordButton.setOnClickListener {
            if (passwordEditText.transformationMethod is PasswordTransformationMethod) {
                // 비밀번호가 숨겨져 있을 때는 보이게 합니다.
                passwordEditText.transformationMethod = null
                showPasswordButton.isSelected = true // 상태를 변경합니다.
            } else {
                // 비밀번호가 보이는 상태일 때는 숨깁니다.
                passwordEditText.transformationMethod = PasswordTransformationMethod.getInstance()
                showPasswordButton.isSelected = false // 상태를 변경합니다.
            }
        }

        val sharedPrefManager = SharedPrefManager(this)

        if (sharedPrefManager.isCheckAutoLogin()) {
            val username = sharedPrefManager.getSavedId()
            val password = sharedPrefManager.getSavedPassword()
            sendLoginRequest(this, username!!, password!!)
        }

        // 로그인 버튼 클릭 이벤트 설정
        loginButton.setOnClickListener {
            // 사용자 이름과 비밀번호 가져오기
            val username = usernameEditText.text.toString()
            val password = passwordEditText.text.toString()
            val keepLogin = keepLoginCheckBox.isChecked
            // 로그인 요청 보내기
            sendLoginRequest(this, username, password, keepLogin)
        }

        // 회원가입 버튼 클릭 이벤트 설정
        registerButton.setOnClickListener {
            // RegisterActivity로 이동
            val intent = Intent(this, RegisterActivity::class.java)
            startActivity(intent)
        }
    }
}