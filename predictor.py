"""Portable prediction from the exact deployed regression coefficients."""
import json
import math
from pathlib import Path

def load_model():
    return json.loads(Path(__file__).with_name('model.json').read_text(encoding='utf-8'))

def predict(model, inputs):
    numbers = {}
    for key in model['numeric']:
        try:
            value = float(inputs[key])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f'{key}: enter a number.') from None
        bounds = model['limits'][key]
        if not math.isfinite(value) or not bounds['min'] <= value <= bounds['max']:
            raise ValueError(f"{key}: use a value between {bounds['min']:g} and {bounds['max']:g}.")
        numbers[key] = value
    for key in model['categorical']:
        if inputs.get(key) not in model['categories'][key]:
            raise ValueError(f'{key}: select a listed option.')
    for key in ['bedrooms','rooms','full_baths','half_baths','year_built','fireplaces','sale_year']:
        if not numbers[key].is_integer():
            raise ValueError(f'{key}: enter a whole number.')
    if numbers['sale_year'] not in model['years']:
        raise ValueError('Select a historical sale year from 2022 to 2025.')
    if numbers['year_built'] > numbers['sale_year']:
        raise ValueError('Year built must be no later than the sale year.')
    if numbers['rooms'] < numbers['bedrooms']:
        raise ValueError('Total rooms must include at least all bedrooms.')
    x = [1.0] + [(numbers[k]-model['medians'][k])/model['scales'][k] for k in model['numeric']]
    for key in model['categorical']:
        x.extend(float(inputs[key] == option) for option in model['categories'][key][1:])
    log_price = sum(v*b for v,b in zip(x,model['coefficients'])) + math.log(model['smearing_factor'])
    try:
        estimate = math.exp(log_price)
        low = math.exp(log_price-model['log_radius'])
        high = math.exp(log_price+model['log_radius'])
    except OverflowError:
        raise ValueError('These details cannot produce a valid estimate.') from None
    if not all(math.isfinite(v) for v in [estimate,low,high]):
        raise ValueError('These details cannot produce a valid estimate.')
    unusual = [k for k in numbers if k != 'sale_year' and not model['limits'][k]['p01'] <= numbers[k] <= model['limits'][k]['p99']]
    return {'estimate':estimate, 'low':low, 'high':high, 'unusual':unusual}
