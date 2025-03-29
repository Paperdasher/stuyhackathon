import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stock Portfolio Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.Font(None, 36)

# Helper functions
def draw_text(screen, text, x, y, color=BLACK, font=FONT):
    """Draws text on the screen."""
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        draw_text(screen, self.text, self.rect.x + 10, self.rect.y + 10, self.text_color)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# Classes for game logic
class Company:
    def __init__(self, name, category, price, scenarios_owned, scenarios_not_owned):
        self.name = name
        self.category = category
        self.price = price
        self.previous_price = price  # Store the previous price for price change calculations
        self.scenarios_owned = scenarios_owned
        self.scenarios_not_owned = scenarios_not_owned
        
        self.owned_stocks = 0

    def update_price(self):
        """Simulate stock price fluctuation based on category."""
        self.previous_price = self.price
        if self.category == "emerging":
            change = random.uniform(-0.2, 0.5)
        elif self.category == "fading":
            change = random.uniform(-0.3, 0.1)
        else:
            change = random.uniform(-0.1, 0.1)
        self.price += self.price * change
        self.price = max(round(self.price, 2), 1)

    def choose_scenario(self, owned):
        """Choose a scenario for the company and apply the effect."""
        scenarios = self.scenarios_owned if owned else self.scenarios_not_owned
        scenario = random.choice(scenarios)
        effect = ""
        additional_effect = ""
        color = GREEN if scenarios.index(scenario) == 0 else RED
        if scenarios.index(scenario) == 0:  # Positive impact
            increase_percentage = random.uniform(0.1, 0.3)  # 10% to 30% increase
            self.price += self.price * increase_percentage
            self.price = round(self.price, 2)
            effect = f"Scenario: {scenario} - Stock price increased by {round(increase_percentage * 100, 1)}%"
            additional_increase = random.uniform(0.1,0.3)
            self.price += self.price * additional_increase
            self.price = round(self.price, 2)
            additional_effect = f" Additional increase: {round(additional_increase * 100, 1)}%"
            return effect, additional_effect, color
        elif scenarios.index(scenario) == 1:  # Negative impact
            decrease_percentage = random.uniform(0.1, 0.3)  # 10% to 30% decrease
            self.price -= self.price * decrease_percentage
            self.price = max(round(self.price, 2), 1)
            effect = f"Scenario: {scenario} - Stock price decreased by {round(decrease_percentage * 100, 1)}%"
            additional_decrease = random.uniform(0.1,0.3)
            self.price -= self.price * additional_decrease
            self.price = max(round(self.price, 2), 1)
            additional_effect = f" Additional decrease: {round(additional_decrease * 100, 1)}%"
            return effect, additional_effect, color
        return f"Scenario: No significant price change.", "", BLACK

class Portfolio:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.stocks = {}

    def buy(self, company, quantity):
        cost = company.price * quantity
        if self.balance >= cost:
            if company.name in self.stocks:
                self.stocks[company.name]['quantity'] += quantity
            else:
                self.stocks[company.name] = {'quantity':quantity}
            self.balance -= cost
            company.owned_stocks += quantity
            return f"Bought {quantity} shares of {company.name}."
        return "Not enough funds."
    
    def sell(self, company, quantity):
        if company.name in self.stocks and self.stocks[company.name]['quantity'] >= quantity:
            revenue = company.price * quantity
            self.stocks[company.name]['quantity'] -= quantity
            self.balance += revenue
            company.owned_stocks -= quantity
            if self.stocks[company.name]['quantity'] == 0:
                del self.stocks[company.name]
            return f"Sold {quantity} shares of {company.name}."
        return "You don't own enough of this stock to sell."
    
    def get_owned_stocks(self):
        """Returns a list of owned stocks."""
        return [(name, data['quantity']) for name, data in self.stocks.items()]

    def calculate_portfolio_value(self, companies):
        """Calculates the current value of the portfolio."""
        total_value = self.balance
        for name, data in self.stocks.items():
            company = next((c for c in companies if c.name == name), None)
            if company:
                total_value += company.price * data['quantity']
        return total_value

# Game states
MAIN_MENU = "main_menu"
BUY_PAGE = "buy_page"
SCENARIO_PAGE = "scenario_page"
SELL_PAGE = "sell_page"

def main():
    # Initialize game variables
    running = True
    state = MAIN_MENU
    year = 1
    portfolio = Portfolio(initial_balance=10000)
    total_years = 10 #total game years
    years_passed = 0

    companies = [
        Company("Orange", "large", 5000.00, ["New product launch", "Market competition"], "Technology"),
        Company("Ezzon", "large", 1000.00, ["Government contract", "Antitrust investigation"], "Natural Oil"),
        Company("Bamazon", "large", 2000.00, ["Holiday sales spike", "Warehouse strike"], "E-commerce"),
        Company("Planetdollars", "large", 100.00, ["New lineup of drinks popular", "Boycott due to human rights concerns"], "Food & Beverage"),
        Company("RiseX", "emerging", 50.00, ["Venture capital funding", "Product failure"], "Startups"),
        Company("GreenTech", "emerging", 75.00, ["Environmental grant", "Technology setback"], "Renewable Energy"),
        Company("FossilCorp", "fading", 50.00, ["Cost-cutting measures", "Loss of major client"], "Energy"),
        Company("RetailCo", "small", 100.00, ["Local expansion", "Supply chain issues"], "Retail"),
        Company("BioFuture", "emerging", 300.00, ["Breakthrough drug", "Clinical trial failure"], "Biotechnology"),
        Company("TechGiant", "large", 1200.00, ["New AI product", "Data breach"], "Technology"),
        Company("LegacyInd", "fading", 30.00, ["Asset liquidation", "Bankruptcy rumors"], "Manufacturing"),
    ]
    scenario_text = ""
    additional_scenario_text = ""
    scenario_colors = []

    # Buttons
    buy_page_button = Button(WIDTH // 2 - 75, HEIGHT // 2 - 50, 150, 50, "Buy Stocks", GREEN, WHITE, action="buy_page")
    sell_page_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 10, 150, 50, "Sell Stocks", RED, WHITE, action="sell_page")
    next_year_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 70, 150, 50, "Next Year", BLACK, WHITE, action="next_year")
    back_button = Button(WIDTH // 2 - 75, HEIGHT - 100, 150, 50, "Back", RED, WHITE, action="back")

    buy_buttons = [
        Button(600, 100 + i * 50, 150, 40, "Buy", GREEN, WHITE, action=f"buy_{company.name}")
        for i, company in enumerate(companies)
    ]

    sell_buttons = [
        Button(600, 100 + i * 50, 80, 40, "Sell", RED, WHITE, action=f"sell_{company.name}")
        for i, company in enumerate(companies)
    ]
    
    while running:
        screen.fill(WHITE)

        if state == MAIN_MENU:
            draw_text(screen, f"Year: {year}", 10, 10, BLACK)
            draw_text(screen, f"Balance: ${portfolio.balance:.2f}", 10, 50, BLACK)
            draw_text(screen, "Owned Stocks:", 10, 100, BLACK)
            y_offset = 140
            for name, quantity in portfolio.get_owned_stocks():
                draw_text(screen, f"{name}: {quantity} shares", 10, y_offset, BLACK)
                company = next((company for company in companies if company.name == name), None)
                if company:
                    # Calculate the price change
                    price_change = company.price - company.previous_price
                    price_change_percentage = (price_change / company.previous_price) * 100
                    color = GREEN if price_change > 0 else RED
                    price_change_text = f"Change: {round(price_change_percentage, 2)}%"
                    draw_text(screen, price_change_text, 250, y_offset, color)
                y_offset += 30
            buy_page_button.draw(screen)
            sell_page_button.draw(screen)
            next_year_button.draw(screen)

        elif state == BUY_PAGE:
            draw_text(screen, "Buy Stocks", WIDTH // 2 - 100, 50, BLACK)
            for i, company in enumerate(companies):
                draw_text(screen, f"{company.name}: ${company.price:.2f}", 10, 100 + i * 50, BLACK)
                buy_buttons[i].draw(screen)
            back_button.draw(screen)

        elif state == SELL_PAGE:
            draw_text(screen, "Sell Stocks", WIDTH // 2 - 100, 50, BLACK)
            for i, company in enumerate(companies):
                draw_text(screen, f"{company.name}: ${company.price:.2f}", 10, 100 + i * 50, BLACK)
                sell_buttons[i].draw(screen)
            back_button.draw(screen)

        elif state == SCENARIO_PAGE:
            if year == 10:
                if back_button.is_clicked(event):
                    state = MAIN_MENU
                    year += 1
                    years_passed +=1
                    for company in companies:
                        company.update_price()
            else:
                if back_button.is_clicked(event):
                    state = MAIN_MENU
                    for company in companies:
                        company.update_price()
                    # Calculate the portfolio value and display the profit or loss
                    final_value = portfolio.calculate_portfolio_value(companies)
                    profit_loss = final_value - 10000
                    profit_loss_text = f"Final Profit/Loss: ${profit_loss:.2f}"
                    profit_loss_color = GREEN if profit_loss > 0 else RED
                    draw_text(screen, profit_loss_text, WIDTH // 2 - 150, HEIGHT // 2, profit_loss_color)
                    pygame.display.flip()
                    pygame.time.wait(3000)  # Wait for 3 seconds before going back to the main menu
                    pygame.quit()
            
            draw_text(screen, f"Year: {year}", 10, 10, BLACK)
            draw_text(screen, f"Balance: ${portfolio.balance:.2f}", 10, 50, BLACK)
            y_offset = 100
            for i in range(len(scenario_text.split('\n')) -1):
                draw_text(screen, scenario_text.split('\n')[i], 10, y_offset, scenario_colors[i])
                y_offset += 30
            y_offset = 100
            
            back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == MAIN_MENU:
                if buy_page_button.is_clicked(event):
                    state = BUY_PAGE
                elif sell_page_button.is_clicked(event):
                    state = SELL_PAGE
                elif next_year_button.is_clicked(event):
                    state = SCENARIO_PAGE
                    scenario_text = ""
                    additional_scenario_text = ""
                    scenario_colors = []
                    all_owned = True
                    for company in companies:
                        if company.name not in portfolio.stocks:
                            all_owned = False
                            break
                    for company in companies:
                        owned = company.name in portfolio.stocks
                        scenario, additional_effect, color = company.choose_scenario(owned if not all_owned else True)
                        scenario_text += f"{company.name}: {scenario}\n"
                        additional_scenario_text += f"{company.name}: {additional_effect}\n"
                        scenario_colors.append(color)

            elif state == BUY_PAGE:
                for i, button in enumerate(buy_buttons):
                    if button.is_clicked(event):
                        message = portfolio.buy(companies[i], 1)
                        print(message)  # Debugging output
                if back_button.is_clicked(event):
                    state = MAIN_MENU
            elif state == SELL_PAGE:
                for i, button in enumerate(sell_buttons):
                    if button.is_clicked(event):
                        if companies[i].name in portfolio.stocks and portfolio.stocks[companies[i].name]['quantity'] > 0:
                            message = portfolio.sell(companies[i], 1)
                        else:
                            message = f"You don't own any shares of {companies[i].name}."
                        print(message)  # Debugging output
                if back_button.is_clicked(event):
                    state = MAIN_MENU

            elif state == SCENARIO_PAGE:
                if back_button.is_clicked(event):
                    state = MAIN_MENU
                    year += 1
                    for company in companies:
                        company.update_price()

        pygame.display.flip()

if __name__ == "__main__":
    main()