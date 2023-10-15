import numpy as np

def bond_price(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price of a bond from spread and recovery rate
    returns an array of price in absolute value (i.e. for a notional of 1)
    returns nan if default_intensity_plus_interest_rate is null
    """
    one_minus_recovery = np.add(1,-recovery_rate)
    default_intensity = np.divide(spread, one_minus_recovery) # aka hazard rate
    default_intensity_plus_interest_rate = np.add(default_intensity, interest_rate)
    ir_plus_lambda_times_t = np.multiply(default_intensity_plus_interest_rate, maturity)
    discount_to_maturity = np.exp(-ir_plus_lambda_times_t)
    integral = np.divide(np.add(1,-discount_to_maturity), default_intensity_plus_interest_rate)
    sum_discounted_coupon = np.multiply(coupon, integral)
    recovery_discounted = np.multiply(recovery_rate,np.multiply(default_intensity, integral))
    return np.add(np.add(discount_to_maturity, sum_discounted_coupon),recovery_discounted)

def bond_cr01(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the credit spread
    returns an array of CR01 in absolute term
    returns nan if sum of interest rate and default intensity is null
    """
    spread_bump = 1e-4
    spread_plus_1_basis_point = np.add(spread, spread_bump)
    spread_minus_1_basis_point = np.add(spread, -spread_bump)

    price_plus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_plus_1_basis_point, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_minus_1_basis_point, recovery_rate)
    return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / spread_bump / 1e2


def bond_ir01(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the interest rate
    returns an array or IR01 in absolute term
    returns nan if sum of spread and default intensity is null
    """
    ir_bump = 1e-4
    ir_plus_1_basis_point = np.add(interest_rate, ir_bump)
    ir_minus_1_basis_point = np.add(interest_rate, -ir_bump)

    price = bond_price(maturity, coupon, interest_rate, spread, recovery_rate)
    price_plus_1_basis_point = bond_price(maturity, coupon, ir_plus_1_basis_point, spread, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, ir_minus_1_basis_point, spread, recovery_rate)
    return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / ir_bump / 1e2

def bond_spread(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               price: np.array,
               recovery_rate:np.array,
               max_number_of_loop:int = 15) -> np.array:
    """
    vectorized function to compute the credit spread that matches a bond price given in percent for a given recovery rate
    returns an array of spread in absolute value

    """
    # first ensure recovery ate is positive and at least 10% below the bond market price to ensure the spread can be implied
    recovery_rate = np.clip(recovery_rate, 0, np.subtract(np.divide(price,100), 0.1))
    # makes a first estimate of the yield of the bond using bond price, years to maturity and coupon, then substract interest rate to get spread
    spread_guess = np.subtract(np.divide(np.add(coupon, np.divide(np.subtract(100,price), maturity)/100), np.add(price, 100)/2)*100, interest_rate)
    price_theoretical = 100 * bond_price(maturity,coupon, interest_rate, spread_guess, recovery_rate)
    counter = 0
    # from starting spread, iterate the calculatio of the spread using a Newton-Raphson method on the bond price
    while counter < max_number_of_loop and np.max(np.abs(np.subtract(price_theoretical, price))) > 1e-6:
        cr01 = bond_cr01(maturity, coupon, interest_rate, spread_guess, recovery_rate)
        spread_guess = spread_guess + np.divide(np.subtract(price, price_theoretical), cr01) / 10_000
        price_theoretical = 100 * bond_price(maturity,coupon, interest_rate, spread_guess, recovery_rate)
        counter += 1
    return spread_guess