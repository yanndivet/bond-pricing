import numpy as np

def continuous_to_discrete(r: np.array, n = np.array) -> np.array:
    r_over_n = np.divide(r, n)
    return np.multiply(n, np.expm1(r_over_n))

def discrete_to_continuous(r: np.array, n = np.array) -> np.array:
    r_over_n = np.divide(r, n)
    return np.multiply(n, np.log1p(r_over_n))

def bond_price_from_yield(t:np.array, ytm:np.array, c:np.array, freq:np.array) -> np.array:
    """
    
    Parameters
    ----------
    t : np.array
        year to maturity.
    ytm : np.array
        yield to maturity.
    c : np.array
        yearly coupon rate in absolute term (5% -> 0.05).
    freq : np.array
        number of coupon per year.

    Returns
    -------
    return clean price in percent, yieldDelta (DV01) in percent

    """
    freq_t = np.multiply(t, freq)
    ytm_on_freq = np.divide(ytm, freq)
    coupon_on_freq = np.divide(c, freq)
    coupon_on_yield = coupon_on_freq/ytm_on_freq
    aux = np.power(1+ytm_on_freq, -freq_t)
    coupon_on_yield_one_minus_aux = coupon_on_yield*(1-aux)
    price = 100*(aux +coupon_on_yield_one_minus_aux)
    delta_aux = -np.multiply(t, aux) / (1+ytm_on_freq)
    gamma_aux = np.multiply(t, aux) * np.divide(1+freq_t, freq) / np.square((1+ytm_on_freq))
    yieldDelta = (delta_aux*(1-coupon_on_yield)-np.divide(coupon_on_yield_one_minus_aux, ytm))
    yieldGamma = 0.01*(gamma_aux * (1-coupon_on_yield) + 2 * delta_aux * np.divide(coupon_on_yield, ytm) + 2 * np.divide(coupon_on_yield_one_minus_aux, np.square(ytm)))
    
    return price, yieldDelta, yieldGamma

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
               recovery_rate:np.array,
               delta:bool=True) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the credit spread
    returns an array of CR01 in absolute term if delta is True, else returns an array of CR_gamma instead
    returns nan if sum of interest rate and default intensity is null
    """
    spread_bump = 1e-4
    spread_plus_1_basis_point = np.add(spread, spread_bump)
    spread_minus_1_basis_point = np.add(spread, -spread_bump)

    price_plus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_plus_1_basis_point, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, interest_rate, spread_minus_1_basis_point, recovery_rate)
    if delta:
        return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / spread_bump / 1e2
    else:
        price = bond_price(maturity, coupon, interest_rate, spread, recovery_rate)
        return (price_plus_1_basis_point + price_minus_1_basis_point - 2 * price) /  np.square(spread_bump) / 1e4


def bond_ir01(maturity: np.array,
               coupon:np.array,
               interest_rate:np.array,
               spread: np.array,
               recovery_rate:np.array,
               delta:bool=True) -> np.array:
    """
    vectorized function to compute the price sensitivity of a bond for a bump of 1 basis point of the interest rate
    returns an array or IR01 in absolute term if delta is True, else returns an array of IR_gamma instead
    returns nan if sum of spread and default intensity is null
    """
    ir_bump = 1e-4
    ir_plus_1_basis_point = np.add(interest_rate, ir_bump)
    ir_minus_1_basis_point = np.add(interest_rate, -ir_bump)

    price = bond_price(maturity, coupon, interest_rate, spread, recovery_rate)
    price_plus_1_basis_point = bond_price(maturity, coupon, ir_plus_1_basis_point, spread, recovery_rate)
    price_minus_1_basis_point = bond_price(maturity, coupon, ir_minus_1_basis_point, spread, recovery_rate)
    if delta:
        return (price_plus_1_basis_point - price_minus_1_basis_point) / 2 / ir_bump / 1e2
    else:
        price = bond_price(maturity, coupon, interest_rate, spread, recovery_rate)
        return (price_plus_1_basis_point + price_minus_1_basis_point - 2 * price) /  np.square(ir_bump) / 1e4


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
