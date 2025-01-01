Add-Type -AssemblyName System.Windows.Forms
# Получаем начальное положение курсора
$p1 = [System.Windows.Forms.Cursor]::Position

# Ожидаем 10 секунд
Start-Sleep -Seconds 5

# Получаем положение курсора после 10 секунд
$p2 = [System.Windows.Forms.Cursor]::Position

# Проверяем, изменилось ли положение курсора
if($p1.X -eq $p2.X -and $p1.Y -eq $p2.Y) {
    # Если курсор не двигался
    $result = $false
} else {
    # Если курсор двигался
    $result = $true
}

# Выводим результат
$result | Out-File -FilePath "C:\Users\FokinKV\PycharmProjects\auto_close_jira_alert\result.txt" -Encoding utf8
