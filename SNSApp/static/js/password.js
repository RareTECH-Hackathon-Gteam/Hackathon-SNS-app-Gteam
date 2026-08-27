function togglePassword(inputId = 'passwordInput', iconId = 'eyeIcon') {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);

  if (input && icon){
    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash'); // 斜線付きの目に変更
    } else {
      input.type = 'password';
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye'); // 通常の目に戻す
    }
  }
}