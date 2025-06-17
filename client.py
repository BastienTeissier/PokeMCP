from fastmcp import Client
from google import genai
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class PokemonChatCLI:
    def __init__(self):
        self.config = {
            "mcpServers": {
                "pokemcp": {
                    "url": "http://localhost:9999/sse",
                    "transport": "sse"
                },
            }
        }
        self.client = Client(self.config)
        self.gemini_client = genai.Client()
        self.console = Console()
        self.conversation_history = []

    def show_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = Text()
        welcome_text.append("🔥 Welcome to Pokemon MCP Chat! 🔥\n\n", style="bold red")
        welcome_text.append("I'm your Pokemon assistant powered by MCP tools.\n", style="cyan")
        welcome_text.append("Ask me anything about Pokemon!\n\n", style="cyan")
        welcome_text.append("Commands:\n", style="bold yellow")
        welcome_text.append("• Type 'quit' or 'exit' to leave\n", style="white")
        welcome_text.append("• Ask about any Pokemon for detailed information\n", style="white")
        welcome_text.append("• I can access live Pokemon data through MCP tools\n\n", style="white")
        
        panel = Panel(welcome_text, title="Pokemon MCP Chat", border_style="bright_blue")
        self.console.print(panel)

    def get_user_input(self):
        """Get user input with a nice prompt"""
        try:
            return input("\n🎯 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            return "quit"

    async def process_message(self, message):
        """Process user message with Gemini + MCP tools"""
        try:
            # Add user message to conversation history
            self.conversation_history.append(f"User: {message}")
            
            # Show loading indicator
            with self.console.status("[bold green]Thinking and searching Pokemon data..."):
                response = await self.gemini_client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=message,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.3,
                        tools=[self.client.session],
                    ),
                )
            
            # Add AI response to conversation history
            self.conversation_history.append(f"Assistant: {response.text}")
            
            return response.text
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.console.print(f"[bold red]Error:[/bold red] {error_msg}")
            return None

    def display_response(self, response):
        """Display AI response with nice formatting"""
        if response:
            response_text = Text()
            response_text.append("🤖 Assistant: ", style="bold green")
            response_text.append(response, style="white")
            
            panel = Panel(response_text, border_style="green")
            self.console.print(panel)

    def is_quit_command(self, message):
        """Check if user wants to quit"""
        return message.lower() in ['quit', 'exit', 'bye', 'goodbye']

    async def start_chat(self):
        """Main chat loop"""
        self.show_welcome()
        
        async with self.client:
            while True:
                try:
                    # Get user input
                    user_input = self.get_user_input()
                    
                    if not user_input:
                        continue
                    
                    # Check for quit command
                    if self.is_quit_command(user_input):
                        self.console.print("\n[bold cyan]Thanks for chatting! Goodbye! 👋[/bold cyan]")
                        break
                    
                    # Process the message
                    response = await self.process_message(user_input)
                    
                    # Display the response
                    self.display_response(response)
                    
                except Exception as e:
                    self.console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
                    self.console.print("[yellow]Type 'quit' to exit safely.[/yellow]")

async def main():
    chat_cli = PokemonChatCLI()
    await chat_cli.start_chat()

if __name__ == "__main__":
    asyncio.run(main())