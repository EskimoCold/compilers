namespace Lab01;

/// <summary>
/// A lexical token: kind (<see cref="TokenType"/>) and the exact text span.
/// </summary>
public sealed class Token
{
    public TokenType Type { get; }
    public string Value { get; }
    public int Position { get; }

    public Token(TokenType type, string value, int position)
    {
        Type = type;
        Value = value;
        Position = position;
    }

    public override string ToString() => $"Token(Type: {Type}, Value: '{Value}') at {Position}";
}
