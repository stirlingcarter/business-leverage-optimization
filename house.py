import uuid

SUPPLEMENTAL_INC_PER_MO = 1800*2 - 500 - 1500
MOS_SI_REC = 0
STARTING_CASH = 100000
MORTGAGE_LENGTHS = 30
APR = .03
APR_FACTOR = 1.93
HOME_VALUE_TARGET = 160000
DOWN_PAYMENT_PERCENTAGE = .2
RI_YRLY_APPR = .03
ETF_YRLY_DRAW = .04
MONTHS_IN_YEAR = 12
MIN_PURCHASE_GAP_MOS = 12
MAX_HOUSES = 7
ADJUST_RENT_TO_MARKET = "ON_TURNOVER" #ON_TURNOVER or PERIODICLY
RENT_ADJUST_PERIOD_MOS = -1
AVG_TURNOVER_MOS = 50
RENT_PER_VALUE = .01

CAPEX_PER_RENT = .10
MAINT_PER_RENT = .10
MANAGEMENT_PER_RENT =.10
INSURANCE_PER_VALUE_PER_MO = .018 / 12
PROPERTY_TAX_PER_VALUE_PER_MO = .0136 / 12

TARGET_MO_INC = 3000


class House:

    def __init__(self, cost, down):
        self.appr_value = cost
        self.initial_value = cost
        self.rent = self.initial_value * RENT_PER_VALUE
        self.equity = down
        self.age_months = 0
        self.p_owed = cost - down
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        self.NOI = self.getNOI()

        
    #a monthly step
    def step(self):
    
        #age
        self.age_months += 1
        #adjust rent
        if  ADJUST_RENT_TO_MARKET == "ON_TURNOVER" and self.age_months % AVG_TURNOVER_MOS == 0:
            self.rent = self.appr_value * RENT_PER_VALUE
        elif ADJUST_RENT_TO_MARKET == "PERIODICLY" and self.age_months % RENT_ADJUST_PERIOD_MOS == 0:
            self.rent = self.appr_value * RENT_PER_VALUE
            
        #calculate and adjust p and i
        if self.equity < self.initial_value:
            interest = APR/MONTHS_IN_YEAR*self.p_owed
            principal = self.MONTHLY - interest
            self.p_owed -= principal
            self.equity += principal
            self.i_owed -= interest
        #acct for apr
        self.appr_value *= (1 + (RI_YRLY_APPR/MONTHS_IN_YEAR))#.04 is yrly RI ^
    
    def getNOI(self):
    
        NOI = self.rent
        NOI -= self.rent * CAPEX_PER_RENT
        NOI -= self.rent * MAINT_PER_RENT
        NOI -= self.rent * MANAGEMENT_PER_RENT
        NOI -= self.appr_value * PROPERTY_TAX_PER_VALUE_PER_MO
        NOI -= self.appr_value * INSURANCE_PER_VALUE_PER_MO
        
        if self.equity < self.initial_value:
            NOI -= self.MONTHLY
        return NOI
        
    def get_monthly_income(self):
        if self.age_months % 12 == 0:
            self.NOI = self.getNOI()
        return self.NOI
    
    def print_house(self):
        print("\n")
        print("RED: " + str(round(self.getRed(),2)) + "% of current value, or $" + str(self.p_owed))
        print("VALUE: " + str(self.appr_value))
        print("BRINGIN IN MONTHLY: " + str(self.get_monthly_income()))
        print("\n")

    def refi(self):
        down = self.appr_value * DOWN_PAYMENT_PERCENTAGE
        out = self.appr_value - self.initial_value + self.equity - down
        self.initial_value = self.appr_value
        cash_loan_out = self.appr_value - down
        self.equity = down
        self.p_owed = cash_loan_out
        total_owed = self.p_owed + self.p_owed/APR_FACTOR
        self.i_owed = total_owed - self.p_owed
        self.MONTHLY = total_owed/MONTHS_IN_YEAR/MORTGAGE_LENGTHS
        return out
        
    def payOff(self):
        owed = self.p_owed
        self.p_owed = 0
        self.equity = self.initial_value
        return owed
    
    def getGreen(self):
        green = self.appr_value - self.p_owed
        return 100 - self.getRed()
        
    def getRed(self):
        if self.equity >= self.initial_value:
            return 0
        else:
            return 100 / self.appr_value * self.p_owed


def run():

    u = str(uuid.uuid1()).split("-")[0]
    print(u)


    cash = STARTING_CASH
    monthly_income = 0
    houses = []
    months = 0
    mos_since_last_purchase = MIN_PURCHASE_GAP_MOS+1

    while (monthly_income < TARGET_MO_INC and months < 360) and cash > 0:
        if months < MOS_SI_REC:
            cash += SUPPLEMENTAL_INC_PER_MO
        months += 1


        down = HOME_VALUE_TARGET * DOWN_PAYMENT_PERCENTAGE

        for h in houses:
            h.step()
            if h.equity + h.appr_value - h.initial_value > 2 * down and len(houses) < MAX_HOUSES:
                print("\n\n\nREFIIIIIII\n\n")
                cash += h.refi()
        
        if len(houses) == MAX_HOUSES:
            for h in houses:
            
                if h.p_owed != 0 and h.p_owed < cash:
                    print("PAID OFF")
                    cash -= h.payOff()

        cash += monthly_income
        new_monthly_income = 0
        for h in houses:
            
            new_monthly_income += h.get_monthly_income()
        monthly_income = new_monthly_income + cash*ETF_YRLY_DRAW/MONTHS_IN_YEAR
        
        print("\n")
        print("CASH: " + str(cash))
        print("MOS: " + str(months))
        print("MONTHLY: " + str(monthly_income))
        print("\n")
        mos_since_last_purchase += 1
        if cash > down and len(houses) < MAX_HOUSES and mos_since_last_purchase >= MIN_PURCHASE_GAP_MOS:
            print("PURCHASED")

            houses.append(House(HOME_VALUE_TARGET,down))
            cash -= down
            mos_since_last_purchase = 0
            

        
        if months%MONTHS_IN_YEAR == 0:
            print("----------------------------------------------------------------------VVV-YEAR" + u + str(months//MONTHS_IN_YEAR)+"-VVV--------------------------------------------------------------")
            for i in range(len(houses)):
                print("\n")
                print("HOUSE " + str(i) + ":")
                houses[i].print_house()
            print("----------------------------------------------------------------------^^^-YEAR"+str(months//MONTHS_IN_YEAR)+"-^^^------------------------------------------------------------")
        
    if cash <= 0:
        print("YA LOSE")


    print("YEAR" + u)
    
    return [months, u]
    
run()
opt = [0,0]
opt_t = 100000000
opt_u = 0
for m in range(1,30):
    MAX_HOUSES = m
    for v in range(50000,1000000,10000):
        HOME_VALUE_TARGET = v
        ans_set = run()
        t = ans_set[0]
        u = ans_set[1]
        if t < opt_t:
            opt[0] = m
            opt[1] = v
            opt_t = t
            opt_u = u
print("\n")
print("\n")
print("-----------------------------------FINAL RESULTS-----------------------------------")

print("OPTIMUM N, V:" + str(opt))
print("ID: " + u)
print("MONTHS to $" + str(TARGET_MO_INC) + " PIPM: " + str(opt_t))
