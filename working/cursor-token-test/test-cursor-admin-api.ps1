$cursorKey = "PASTE_KEY_LOCALLY"

$pair = "${cursorKey}:"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$basic = [Convert]::ToBase64String($bytes)

$headers = @{
    Authorization = "Basic $basic"
}

Invoke-RestMethod `
    -Uri "https://api.cursor.com/teams/members" `
    -Method Get `
    -Headers $headers
