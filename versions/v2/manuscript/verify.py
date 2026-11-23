import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path


def polynomial(value):
    return {(0, 0, 0, 0): Fraction(value)} if value else {}


def variable(position):
    powers = [0, 0, 0, 0]
    powers[position] = 1
    return {tuple(powers): Fraction(1)}


def add(*terms):
    result = {}
    for term in terms:
        for powers, coefficient in term.items():
            result[powers] = result.get(powers, Fraction(0)) + coefficient
    return {powers: coefficient for powers, coefficient in result.items() if coefficient}


def multiply(*factors):
    result = polynomial(1)
    for factor in factors:
        product = {}
        for left_powers, left_coefficient in result.items():
            for right_powers, right_coefficient in factor.items():
                powers = tuple(left + right for left, right in zip(left_powers, right_powers))
                product[powers] = product.get(powers, Fraction(0)) + left_coefficient * right_coefficient
        result = {powers: coefficient for powers, coefficient in product.items() if coefficient}
    return result


def scale(value, term):
    return multiply(polynomial(value), term)


def symbolic_parity_checks():
    half_index = variable(0)
    even_weight = variable(1)
    odd_weight = variable(2)
    radicand = variable(3)
    weighted_square = multiply(radicand, even_weight, even_weight)
    odd_square = multiply(odd_weight, odd_weight)
    combined = add(weighted_square, odd_square)
    two_index = scale(2, half_index)
    previous_odd = add(two_index, polynomial(-1))
    middle = multiply(radicand, even_weight, odd_weight)

    def coefficients(index):
        leading = multiply(index, add(multiply(combined, index), scale(-2, weighted_square), scale(-1, odd_square)))
        lagged = multiply(radicand, add(index, polynomial(-2)), add(multiply(combined, index), scale(-1, weighted_square)))
        return leading, lagged

    leading, lagged = coefficients(two_index)
    factor = multiply(even_weight, add(multiply(add(two_index, polynomial(-2)), weighted_square), multiply(previous_odd, odd_square)))
    assert multiply(leading, even_weight) == multiply(two_index, factor)
    assert add(multiply(middle, odd_weight), multiply(lagged, even_weight)) == multiply(radicand, previous_odd, factor)
    leading, lagged = coefficients(add(two_index, polynomial(1)))
    factor = multiply(odd_weight, add(multiply(two_index, weighted_square), multiply(add(two_index, polynomial(1)), odd_square)))
    assert add(multiply(leading, odd_weight), multiply(middle, even_weight)) == multiply(two_index, factor)
    assert multiply(lagged, odd_weight) == multiply(radicand, previous_odd, factor)
    return 4


def root_inverse_coefficients(radicand_coefficients, degree):
    root = [Fraction(1)]
    for index in range(1, degree + 1):
        target = Fraction(radicand_coefficients.get(index, 0))
        root.append((target - sum(root[inner] * root[index - inner] for inner in range(1, index))) / 2)
    inverse = [Fraction(1)]
    for index in range(1, degree + 1):
        inverse.append(-sum(root[inner] * inverse[index - inner] for inner in range(1, index + 1)))
    for index in range(degree + 1):
        assert sum(root[inner] * root[index - inner] for inner in range(index + 1)) == radicand_coefficients.get(index, int(index == 0))
        assert sum(root[inner] * inverse[index - inner] for inner in range(index + 1)) == int(index == 0)
    return inverse


def symbolic_bridge_checks():
    index = variable(0)
    even_weight = variable(1)
    odd_weight = variable(2)
    radicand = variable(3)
    weighted_square = multiply(radicand, even_weight, even_weight)
    odd_square = multiply(odd_weight, odd_weight)
    combined = add(weighted_square, odd_square)
    current = add(multiply(combined, index), scale(-2, weighted_square), scale(-1, odd_square))
    previous = add(current, scale(-1, combined))
    middle = multiply(radicand, even_weight, odd_weight)
    residual = [multiply(index, current), middle, multiply(radicand, add(index, polynomial(-2)), add(multiply(combined, index), scale(-1, weighted_square))), {}]
    shifted = [{}, multiply(add(index, polynomial(-1)), previous), middle, multiply(radicand, add(index, polynomial(-3)), add(multiply(combined, add(index, polynomial(-1))), scale(-1, weighted_square)))]
    longer = [multiply(even_weight, index), multiply(odd_weight, add(index, polynomial(-2))), multiply(radicand, even_weight, add(index, polynomial(-1))), multiply(radicand, odd_weight, add(index, polynomial(-3)))]
    for current_coefficient, shifted_coefficient, longer_coefficient in zip(residual, shifted, longer):
        assert add(multiply(even_weight, current_coefficient), multiply(odd_weight, shifted_coefficient)) == multiply(current, longer_coefficient)
    return 4


def series_from_root(even_weight, odd_weight, radicand, degree):
    inverse = root_inverse_coefficients({0: 1, 2: radicand}, degree)
    return [even_weight * inverse[index] + (odd_weight * inverse[index - 1] if index else 0) for index in range(degree + 1)]


def paired_coefficients(even_weight, odd_weight, radicand, degree):
    return [(odd_weight if index % 2 else even_weight) * (-Fraction(radicand, 4)) ** (index // 2) * comb(2 * (index // 2), index // 2) for index in range(degree + 1)]


def recurrence_checks(values, even_weight, odd_weight, radicand):
    combined = radicand * even_weight ** 2 + odd_weight ** 2
    for index in range(2, len(values)):
        residual = index * (combined * index - 2 * radicand * even_weight ** 2 - odd_weight ** 2) * values[index]
        residual += radicand * even_weight * odd_weight * values[index - 1]
        residual += radicand * (index - 2) * (combined * index - radicand * even_weight ** 2) * values[index - 2]
        assert residual == 0, (index, even_weight, odd_weight, radicand, residual)
    for index in range(3, len(values)):
        residual = even_weight * index * values[index] + odd_weight * (index - 2) * values[index - 1]
        residual += radicand * even_weight * (index - 1) * values[index - 2]
        residual += radicand * odd_weight * (index - 3) * values[index - 3]
        assert residual == 0


def determinant(matrix):
    values = [list(map(Fraction, row)) for row in matrix]
    result = Fraction(1)
    for column in range(len(values)):
        pivot = next((row for row in range(column, len(values)) if values[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            values[column], values[pivot] = values[pivot], values[column]
            result = -result
        leading = values[column][column]
        result *= leading
        for row in range(column + 1, len(values)):
            multiplier = values[row][column] / leading
            for inner in range(column + 1, len(values)):
                values[row][inner] -= multiplier * values[column][inner]
            values[row][column] = Fraction(0)
    return result


def hankel(values, index):
    return determinant([[values[row + column] for column in range(index + 1)] for row in range(index + 1)])


def lucas(index):
    previous, current = 2, 1
    for step in range(index):
        previous, current = current, previous + current
    return previous


def rational_series(numerator, denominator, degree):
    assert denominator[0] != 0
    values = []
    for index in range(degree + 1):
        target = numerator[index] if index < len(numerator) else 0
        values.append(Fraction(target - sum(denominator[lag] * values[index - lag] for lag in range(1, min(index + 1, len(denominator)))), denominator[0]))
    return values


def convolve(left, right):
    values = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            values[left_index + right_index] += left_value * right_value
    return values


def sibling_checks(primary, unsigned, transformed, inverse):
    degree = 64
    signed_hankel = [1]
    unsigned_hankel = [1]
    quotient = [1]
    exponents = [0]
    for index in range(1, degree + 1):
        half_index = (index + 1) // 2
        delta = 2 if half_index % 3 == 0 else 1
        exponent = index - 1 + int(half_index % 3 == 0)
        exponents.append(exponent)
        magnitude = 2 ** exponent
        cosine_twice = [2, 1, -1, -2, -1, 1][half_index % 6]
        unsigned_hankel.append(2 ** (index - 1) * cosine_twice)
        signed_hankel.append((-1) ** half_index * 2 ** (index - 1) * lucas(2 * half_index))
        quotient.append(Fraction((-1) ** half_index * lucas(2 * half_index), delta))
        assert magnitude == abs(unsigned_hankel[-1])
    assert signed_hankel == rational_series([1, -3, 6, -8], [1, 0, 12, 0, 16], degree)
    quotient_numerator = convolve([1, -1], [1, -2, -5, 2, 9, 0, 9, 2, -5, -2, 1])
    quotient_denominator = convolve([1, 0, 3, 0, 1], [1, 0, -3, 0, 8, 0, -3, 0, 1])
    assert quotient == rational_series(quotient_numerator, quotient_denominator, degree)
    magnitude = list(map(abs, unsigned_hankel))
    assert magnitude == rational_series([1, 1, 2, 4, 8, 32], [1, 0, 0, 0, 0, 0, -64], degree)
    assert magnitude == rational_series([-1, 1, -4, 4, -16], convolve([-1, 2], convolve([1, -2, 4], [1, 2, 4])), degree)
    assert exponents == rational_series([0, 0, 1, 0, 1, 1], convolve([1, -2, 1], convolve([1, -1, 1], [1, 1, 1])), degree)
    shifted = rational_series([1, -4], [1, -2, 4], degree)
    for index in range(degree + 1):
        assert shifted[index] == 2 ** index * [2, 1, -1, -2, -1, 1][(index + 1) % 6]
    for index in range(25):
        assert hankel(primary, index) == signed_hankel[index]
        assert hankel(transformed, index) == signed_hankel[index]
        assert hankel(unsigned, index) == unsigned_hankel[index]
        assert hankel(unsigned[1:], index) == shifted[index]
        assert hankel(inverse, index) == 2 ** index * (-1) ** (index * (index + 1) // 2)
        assert hankel(primary[1:], index) == (-1) ** (index * (index + 1) // 2) * 2 ** index * lucas(index + 1)
    for index in range(1, degree + 1):
        product = Fraction(2 ** index)
        for inner in range(index):
            factor = Fraction(inner + 1, 2 * index)
            product *= factor if inner % 2 == 0 else 1 / factor
        assert product == unsigned[index]
    interleaved = []
    scaled_triangle = []
    for row in range(13):
        values = [comb(row, column // 2) if column % 2 == 0 else comb(row - 1, column // 2) for column in range(2 * row + 1)]
        assert values[row] == unsigned[row]
        interleaved.extend(values)
        scaled = [value * 2 ** column for column, value in enumerate(values)]
        assert scaled[row] == 2 ** row * unsigned[row]
        assert scaled[-1] == 4 ** row
        scaled_triangle.extend(scaled)
    assert sum(Fraction(1, magnitude[index]) for index in range(6)) / (1 - Fraction(1, 64)) == Fraction(62, 21)
    source_data = json.loads(Path(__file__).with_name('source-data.json').read_text())
    sequences = {'A128057': primary, 'A128014': unsigned, 'A128058': transformed, 'A128056': signed_hankel, 'A128053': quotient, 'A128054': exponents, 'A128055': magnitude, 'A128018': shifted, 'A098331': inverse, 'A249095': interleaved, 'A249307': scaled_triangle, 'A249308': [2 ** index * value for index, value in enumerate(unsigned)]}
    matched = {}
    for identifier, sequence in sequences.items():
        record = source_data[identifier]
        count = min(len(sequence), len(record['coefficients']))
        assert sequence[:count] == record['coefficients'][:count], identifier
        matched[identifier] = {'revision': record['revision'], 'count': count, 'source_prefix_length': len(record['coefficients'])}
    assert source_data['A128017']['coefficients'][1] == 2
    assert unsigned_hankel[1] == 1
    assert quotient[1] == -3
    return {'determinant_indices': {'first': 0, 'last': 24, 'count_per_sequence': 25, 'sequences': 6}, 'rational_generating_function_degree': degree, 'unsigned_product_degree': degree, 'interleaved_triangle_rows': {'first': 0, 'last': 12}, 'source_prefix_matches': matched, 'counterexamples': {'A128053_printed_odd_sign': {'index': 1, 'printed_formula': 3, 'quotient': -3}, 'A128014_odd_abelian_squares': {'length': 1, 'count': 0, 'sequence': 1}, 'A128017_unsigned_Hankel_identification': {'index': 1, 'entry': 2, 'determinant': 1}, 'A249095_odd_column_index': {'row': 1, 'column': 1, 'printed_formula': 0, 'triangle': 1}, 'A249307_right_endpoint': {'row': 1, 'last_column': 2, 'printed_column': 3, 'right_edge': 4}}}


def main():
    polynomial_checks = symbolic_parity_checks() + symbolic_bridge_checks()
    primary = series_from_root(Fraction(1), Fraction(1), Fraction(4), 128)
    assert primary == paired_coefficients(1, 1, 4, 128)
    assert primary[:10] == [1, 1, -2, -2, 6, 6, -20, -20, 70, 70]
    long_primary = paired_coefficients(1, 1, 4, 512)
    recurrence_checks(long_primary, 1, 1, 4)
    parameters = [(1, 1, 4), (1, 1, -4), (0, 1, 4), (1, 0, 4), (0, 0, 0), (1, 1, 0), (1, 1, -1), (2, 3, Fraction(-9, 4)), (Fraction(2, 3), Fraction(-5, 7), Fraction(11, 5)), (-2, -3, -5)]
    for even_weight, odd_weight, radicand in parameters:
        even_weight, odd_weight, radicand = map(Fraction, (even_weight, odd_weight, radicand))
        values = series_from_root(even_weight, odd_weight, radicand, 64)
        assert values == paired_coefficients(even_weight, odd_weight, radicand, 64)
        recurrence_checks(values, even_weight, odd_weight, radicand)
    unsigned = series_from_root(Fraction(1), Fraction(1), Fraction(-4), 64)
    assert unsigned == [abs(value) for value in primary[:65]]
    transformed = [sum(comb(index, inner) * primary[inner] for inner in range(index + 1)) for index in range(65)]
    inverse = root_inverse_coefficients({0: 1, 1: -2, 2: 5}, 64)
    assert transformed == [sum(inverse[:index + 1]) for index in range(65)]
    for index in range(65):
        double_sum = sum(sum((-1) ** inner * comb(outer, inner) * comb(outer - inner, inner) for inner in range(outer // 2 + 1)) for outer in range(index + 1))
        assert transformed[index] == double_sum
    for index in range(3, 65):
        assert index * transformed[index] + (1 - 3 * index) * transformed[index - 1] + (7 * index - 6) * transformed[index - 2] + 5 * (1 - index) * transformed[index - 3] == 0
    primary_digest = hashlib.sha256(','.join(str(int(value)) for value in primary).encode()).hexdigest()
    siblings = sibling_checks(primary, unsigned, transformed, inverse)
    print(json.dumps({'status': 'pass', 'arithmetic': 'exact integers and rational numbers', 'polynomial_identities': polynomial_checks, 'root_inverse_degree': 128, 'original_recurrence_indices': {'first': 2, 'last': 512, 'count': 511}, 'parameter_cases': len(parameters), 'parameter_degree': 64, 'unsigned_degree': 64, 'binomial_transform_degree': 64, 'binomial_double_sum_degree': 64, 'binomial_recurrence_indices': {'first': 3, 'last': 64}, 'primary_coefficients_0_through_128_sha256': primary_digest, 'siblings': siblings, 'coverage': {'polynomial_identities': 'Exact symbolic factorizations in four indeterminates', 'coefficient_checks': 'Finite complements to the written universal proofs', 'hankel_transform': 'Written determinant proofs and exact finite checks'}}, indent=2))


if __name__ == '__main__':
    main()
