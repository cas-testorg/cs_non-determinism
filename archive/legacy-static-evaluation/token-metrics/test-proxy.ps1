$body = @{
    model    = "gpt-5.4"
    messages = @( @{ role = "user"; content = "Say hello in one sentence." } )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 10

Get-Content .\token_usage.jsonl -Tail 2
