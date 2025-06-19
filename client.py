import getpass

from fastmcp import Client
from google import genai
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from auth.client_auth import ClientAuth


class PokemonChatCLI:
    def __init__(self):
        self.auth = ClientAuth()
        self.token = None
        self.config = {
            "mcpServers": {
                "pokemcp": {"url": "http://localhost:9999/sse", "transport": "sse"},
            }
        }
        self.client = None
        self.gemini_client = genai.Client()
        self.console = Console()
        self.conversation_history = []

    def show_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = Text()
        welcome_text.append("🔥 Welcome to Pokemon MCP Chat! 🔥\n\n", style="bold red")
        welcome_text.append(
            "I'm your Pokemon assistant powered by MCP tools.\n", style="cyan"
        )
        welcome_text.append("Ask me anything about Pokemon!\n\n", style="cyan")
        welcome_text.append("Commands:\n", style="bold yellow")
        welcome_text.append("• Type 'quit' or 'exit' to leave\n", style="white")
        welcome_text.append("• Type 'login' to authenticate\n", style="white")
        welcome_text.append("• Type 'logout' to sign out\n", style="white")
        welcome_text.append(
            "• Ask about any Pokemon for detailed information\n", style="white"
        )
        welcome_text.append(
            "• I can access live Pokemon data through MCP tools\n\n", style="white"
        )

        # Show authentication status
        user_info = self.auth.get_user_info()
        if user_info and user_info.get("has_token"):
            welcome_text.append(
                f"✅ Authenticated as: {user_info.get('email', 'Unknown')}\n",
                style="green",
            )
        else:
            welcome_text.append(
                "⚠️  Not authenticated (some features may be limited)\n", style="yellow"
            )

        panel = Panel(
            welcome_text, title="Pokemon MCP Chat", border_style="bright_blue"
        )
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
            with self.console.status(
                "[bold green]Thinking and searching Pokemon data..."
            ):
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
        return message.lower() in ["quit", "exit", "bye", "goodbye"]

    def is_auth_command(self, message):
        """Check if user wants to authenticate"""
        return message.lower() in ["login", "signin", "auth", "authenticate"]

    def is_logout_command(self, message):
        """Check if user wants to logout"""
        return message.lower() in ["logout", "signout"]

    async def start_chat(self):
        """Main chat loop with authentication"""
        # Ensure authentication is set up
        if not await self.ensure_authenticated():
            return

        self.show_welcome()

        if self.client is None:
            self.console.print("[red]❌ Failed to initialize MCP client[/red]")
            return

        async with self.client:
            while True:
                try:
                    # Get user input
                    user_input = self.get_user_input()

                    if not user_input:
                        continue

                    # Check for quit command
                    if self.is_quit_command(user_input):
                        self.console.print(
                            "\n[bold cyan]Thanks for chatting! Goodbye! 👋[/bold cyan]"
                        )
                        break

                    # Check for authentication commands
                    if self.is_auth_command(user_input):
                        await self.handle_login()
                        continue

                    if self.is_logout_command(user_input):
                        self.handle_logout()
                        continue

                    # Process the message
                    response = await self.process_message(user_input)

                    # Display the response
                    self.display_response(response)

                except Exception as e:
                    self.console.print(
                        f"[bold red]Unexpected error:[/bold red] {str(e)}"
                    )
                    self.console.print("[yellow]Type 'quit' to exit safely.[/yellow]")

    async def handle_login(self):
        """Handle user login process"""
        self.console.print("\n[bold blue]🔐 Authentication Required[/bold blue]")

        # Check if already authenticated
        user_info = self.auth.get_user_info()
        if user_info and user_info.get("has_token"):
            if Confirm.ask(
                f"Already logged in as {user_info.get('email')}. Login as different user?"
            ):
                self.auth.logout()
            else:
                self.console.print("[green]Already authenticated![/green]")
                return True

        self.console.print("\n[yellow]Please enter your credentials:[/yellow]")

        # Get credentials
        email = Prompt.ask("Email")
        password = getpass.getpass("Password: ")

        # Attempt login
        success = await self.auth.login(email, password)

        if success:
            self.console.print("\n[green]✅ Login successful![/green]")
            # Update client configuration with token
            await self.configure_client_auth()
            return True
        else:
            self.console.print("\n[red]❌ Login failed. Please try again.[/red]")

            # Offer signup option
            if Confirm.ask("Would you like to create a new account?"):
                return await self.handle_signup()
            return False

    async def handle_signup(self):
        """Handle user signup process"""
        self.console.print("\n[bold blue]📝 Create New Account[/bold blue]")

        email = Prompt.ask("Email")
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm Password: ")

        if password != confirm_password:
            self.console.print("[red]❌ Passwords don't match![/red]")
            return False

        success = await self.auth.signup(email, password)

        if success:
            self.console.print(
                "\n[green]✅ Account created! Please check your email for verification.[/green]"
            )
            self.console.print(
                "[yellow]After verification, please login with your credentials.[/yellow]"
            )
            return await self.handle_login()
        else:
            return False

    async def configure_client_auth(self):
        """Configure the MCP client with authentication token"""
        self.token = self.auth.get_stored_token()

        if self.token:
            # Update client configuration with Bearer token
            # Note: This is a simplified example - actual FastMCP auth integration may vary
            auth_config = self.config.copy()
            auth_config["mcpServers"]["pokemcp"]["auth"] = {
                "type": "bearer",
                "token": self.token,
            }
            self.client = Client(auth_config)
        else:
            # Use client without authentication
            self.client = Client(self.config)

    async def ensure_authenticated(self):
        """Ensure user is authenticated before starting chat"""
        try:
            # Check for existing valid token
            self.token = self.auth.get_stored_token()

            if not self.token:
                self.console.print(
                    "[yellow]🔐 Authentication recommended for full features[/yellow]"
                )
                if Confirm.ask("Would you like to login?"):
                    if not await self.handle_login():
                        self.console.print(
                            "[yellow]⚠️  Continuing without authentication[/yellow]"
                        )

            # Configure client (with or without auth)
            await self.configure_client_auth()
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Authentication setup failed: {e}[/red]")
            self.console.print("[yellow]⚠️  Continuing without authentication[/yellow]")
            # Fallback to non-authenticated client
            self.client = Client(self.config)
            return True

    def handle_logout(self):
        """Handle user logout"""
        user_info = self.auth.get_user_info()
        if user_info and user_info.get("has_token"):
            if Confirm.ask(f"Logout from {user_info.get('email', 'current account')}?"):
                self.auth.logout()
                self.token = None
                # Reset client to non-authenticated
                self.client = Client(self.config)
                self.console.print("[green]✅ Logged out successfully[/green]")
        else:
            self.console.print("[yellow]Not currently logged in[/yellow]")
