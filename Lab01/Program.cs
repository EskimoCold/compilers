namespace Lab01;

internal static class Program
{
    private static void Main()
    {
        const string codeExample = """
            var x = 123; print x + 5; print "hello world";
            """;

        var lexer = new Lexer(codeExample);
        var tokens = lexer.Tokenize();

        foreach (var token in tokens)
            Console.WriteLine(token);
    }
}
