import re
import bs4
import math
import time
import random
import base64
import hashlib
from functools import reduce
from typing import Union, List, Optional
from .cubic_curve import Cubic
from .interpolate import interpolate
from .rotation import convert_rotation_to_matrix
from .utils import Math, float_to_hex, is_odd, base64_encode, validate_response
from .constants import INDICES_REGEX, ADDITIONAL_RANDOM_NUMBER, DEFAULT_KEYWORD


class ClientTransaction:

    def __init__(self, home_page_response: bs4.BeautifulSoup, ondemand_file_response: Union[bs4.BeautifulSoup, str], random_keyword: Optional[str] = None, random_number: Optional[int] = None):
        validate_response(home_page_response)
        # validate_response(ondemand_file_response)
        if hasattr(ondemand_file_response, "text"):
            ondemand_file_response = ondemand_file_response.text
        if not isinstance(ondemand_file_response, str):
            raise TypeError(f"invalid ondemand file response")
        self.home_page_response = home_page_response
        self.ondemand_file_response = ondemand_file_response
        self.random_keyword = random_keyword or DEFAULT_KEYWORD
        self.random_number = random_number or ADDITIONAL_RANDOM_NUMBER
        self.row_index, self.key_bytes_indices = self.get_indices(
            self.ondemand_file_response)
        self.key = self.get_key(home_page_response=self.home_page_response)
        self.key_bytes = self.get_key_bytes(key=self.key)
        self.animation_key = self.get_animation_key(
            key_bytes=self.key_bytes, home_page_response=self.home_page_response)

    def get_indices(self, ondemand_file_response: str):
        key_byte_indices = []
        key_byte_indices_match = INDICES_REGEX.finditer(
            str(ondemand_file_response))
        for item in key_byte_indices_match:
            key_byte_indices.append(item.group(2))
        if not key_byte_indices:
            raise Exception("Couldn't get KEY_BYTE indices")
        key_byte_indices = list(map(int, key_byte_indices))
        return key_byte_indices[0], key_byte_indices[1:]

    def get_key(self, home_page_response: bs4.BeautifulSoup) -> str:
        # <meta name="twitter-site-verification" content="mentU...+1yPz..../IcNS+......./RaF...R+b"/>
        element: bs4.Tag = home_page_response.select_one(
            "meta[name='twitter-site-verification']")
        if not element:
            raise Exception(
                "Couldn't get [twitter-site-verification] key from the page source")
        return element.get("content")

    def get_key_bytes(self, key: str) -> List[int]:
        return list(base64.b64decode(bytes(key, 'utf-8')))

    def get_frames(self, home_page_response: bs4.BeautifulSoup) -> bs4.ResultSet:
        # loading-x-anim-0...loading-x-anim-3
        return home_page_response.select("[id^='loading-x-anim']")

    def get_2d_array(self, key_bytes: List[Union[float, int]], home_page_response: bs4.BeautifulSoup, frames: Optional[bs4.ResultSet] = None) -> List[List[int]]:
        if frames is None:
            frames = self.get_frames(home_page_response=home_page_response)
        # return list(list(frames[key[5] % 4].children)[0].children)[1].get("d")[9:].split("C")
        return [[int(x) for x in re.sub(r"[^\d]+", " ", item).strip().split()] for item in list(list(frames[key_bytes[5] % 4].children)[0].children)[1].get("d")[9:].split("C")]

    def solve(self, value, min_val, max_val, rounding: bool) -> Union[float, int]:
        result = value * (max_val-min_val) / 255 + min_val
        return math.floor(result) if rounding else round(result, 2)

    def animate(self, frames: List[int], target_time: float) -> str:
        # from_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[:3]])}"
        # to_color = f"#{''.join(['{:x}'.format(digit) for digit in frames[3:6]])}"
        # from_rotation = "rotate(0deg)"
        # to_rotation = f"rotate({solve(frames[6], 60, 360, True)}deg)"
        # easing_values = [solve(value, -1 if count % 2 else 0, 1, False)
        #                  for count, value in enumerate(frames[7:])]
        # easing = f"cubic-bezier({','.join([str(value) for value in easing_values])})"
        # current_time = round(target_time / 10) * 10

        from_color = [float(item) for item in [*frames[:3], 1]]
        to_color = [float(item) for item in [*frames[3:6], 1]]
        from_rotation = [0.0]
        to_rotation = [self.solve(float(frames[6]), 60.0, 360.0, True)]
        frames = frames[7:]
        curves = [self.solve(float(item), is_odd(counter), 1.0, False)
                  for counter, item in enumerate(frames)]
        cubic = Cubic(curves)
        val = cubic.get_value(target_time)
        color = interpolate(from_color, to_color, val)
        color = [max(0, min(255, value)) for value in color]
        rotation = interpolate(from_rotation, to_rotation, val)
        matrix = convert_rotation_to_matrix(rotation[0])
        # str_arr = [format(int(round(color[i])), '02x') for i in range(len(color) - 1)]
        # str_arr = [format(int(round(color[i])), 'x') for i in range(len(color) - 1)]
        str_arr = [format(round(value), 'x') for value in color[:-1]]
        for value in matrix:
            rounded = round(value, 2)
            if rounded < 0:
                rounded = -rounded
            hex_value = float_to_hex(rounded)
            str_arr.append(f"0{hex_value}".lower() if hex_value.startswith(
                ".") else hex_value if hex_value else '0')
        str_arr.extend(["0", "0"])
        animation_key = re.sub(r"[.-]", "", "".join(str_arr))
        return animation_key

    def get_animation_key(self, key_bytes: List[int], home_page_response: bs4.BeautifulSoup) -> str:
        total_time = 4096
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[12] % 16 * (key_bytes[14] % 16) * (key_bytes[7] % 16)]
        # row_index, frame_time = [key_bytes[2] % 16, key_bytes[2] % 16 * (key_bytes[42] % 16) * (key_bytes[45] % 16)]

        row_index = key_bytes[self.row_index] % 16
        frame_time = reduce(lambda num1, num2: num1*num2,
                            [key_bytes[index] % 16 for index in self.key_bytes_indices])
        frame_time = Math.round(frame_time / 10) * 10
        arr = self.get_2d_array(key_bytes=key_bytes,
                                home_page_response=home_page_response)
        frame_row = arr[row_index]

        target_time = float(frame_time) / total_time
        animation_key = self.animate(frames=frame_row, target_time=target_time)
        return animation_key

    def generate_transaction_id(self, method: str, path: str, home_page_response: Optional[bs4.BeautifulSoup] = None, key: Optional[str] = None, animation_key: Optional[str] = None, time_now: Optional[int] = None) -> str:
        time_now = time_now or math.floor(
            (time.time() * 1000 - 1682924400 * 1000) / 1000)
        time_now_bytes = [(time_now >> (i * 8)) & 0xFF for i in range(4)]
        key = key or self.key or self.get_key(
            home_page_response=home_page_response)
        key_bytes = self.get_key_bytes(key=key)
        animation_key = animation_key or self.animation_key or self.get_animation_key(
            key_bytes=key_bytes, home_page_response=home_page_response)
        # hash_val = hashlib.sha256(f"{method}!{path}!{time_now}bird{animation_key}".encode()).digest()
        hash_val = hashlib.sha256(
            f"{method}!{path}!{time_now}{self.random_keyword}{animation_key}".encode()).digest()
        # hash_bytes = [int(hash_val[i]) for i in range(len(hash_val))]
        hash_bytes = list(hash_val)
        random_num = random.randint(0, 255)
        bytes_arr = [*key_bytes, *time_now_bytes, *
                     hash_bytes[:16], self.random_number]
        out = bytearray(
            [random_num, *[item ^ random_num for item in bytes_arr]])
        return base64_encode(out).strip("=")


if __name__ == "__main__":
    pass
