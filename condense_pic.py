from PIL import Image
import numpy as np

# 1. 将图片转换为比特串（进行下采样）
def image_to_bitstring(image_path, stride_x=3, stride_y=3):
    # 打开图片并转换为RGB模式
    img = Image.open(image_path)
    img = img.convert("RGB")  # 确保是RGB模式

    # 获取图片尺寸
    width, height = img.size

    # 初始化比特串
    bit_string = ''

    # 对图片进行下采样（stride_x, stride_y），将每个4x4块压缩成1个像素
    for y in range(0, height, stride_y):
        for x in range(0, width, stride_x):
            # 获取stride_x x stride_y块的像素
            pixels = []
            for dy in range(stride_y):
                for dx in range(stride_x):
                    if x + dx < width and y + dy < height:
                        pixels.append(img.getpixel((x + dx, y + dy)))

            # 选择该块中最小的RGB值作为代表
            mean_r = np.mean([p[0] for p in pixels])
            mean_g = np.mean([p[1] for p in pixels])
            mean_b = np.mean([p[2] for p in pixels])

            # 判断颜色，如果是红色（假设红色是纯红，没有绿色和蓝色）则记录为1，白色记录为0
            if mean_r > 200 and mean_g < 100 and mean_b < 100:
                bit_string += '1'  # 红色像素
                print(mean_r, mean_g, mean_b)
            elif mean_r > 250 and mean_g > 250 and mean_b > 250:
                bit_string += '0'  # 白色像素
            else:
                bit_string += '1'  # 非红色或白色的像素视为白色（可以根据需求调整）

    return bit_string


# 2. 游程编码：对比特串进行压缩
def run_length_encoding(bit_string):
    encoded = []
    i = 0
    n = len(bit_string)
    
    while i < n:
        count = 1
        # 统计连续相同的比特值
        while i + 1 < n and bit_string[i] == bit_string[i + 1]:
            i += 1
            count += 1
        
        # 将比特值和其出现次数转换为二进制，并补全为8位
        count_bin = f'{count:b}'.zfill(8)  # 转换为二进制并补全为8位
        encoded.append((bit_string[i], count_bin))  # 记录为(值, 二进制长度)
        i += 1  # 移动到下一个不同的比特值
    
    return encoded


# 3. 将游程编码写入文件
def write_encoded_to_file(encoded_data, file_path):
    # 将游程编码写入txt文件，长度用01比特串表示
    with open(file_path, 'w') as file:
        for value, count_bin in encoded_data:
            # 将二进制长度写入文件
            file.write(f"{value} {count_bin}\n")


# 4. 解码游程编码
def run_length_decoding(encoded_data):
    # 解码游程编码
    bit_string = ''
    for value, count_bin in encoded_data:
        count = int(count_bin, 2)  # 将二进制长度转换为整数
        bit_string += value * count  # 将相应的值（'0' 或 '1'）重复 count 次
    return bit_string


# 5. 将比特串恢复为图像数据
def bitstring_to_image(bit_string, width, height, stride_x=2, stride_y=2):
    # 将比特串恢复为图像数据（假设是1bit图像：0是白色，1是红色）
    img_data = np.zeros((height // stride_y, width // stride_x), dtype=np.uint8)
    index = 0
    for y in range(0, height, stride_y):
        for x in range(0, width, stride_x):
            img_data[y // stride_y, x // stride_x] = int(bit_string[index])  # 0 或 1
            index += 1
    
    # 扩展图像数据为原图尺寸
    expanded_img_data = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(0, height, stride_y):
        for x in range(0, width, stride_x):
            if img_data[y // stride_y, x // stride_x] == 1:  # 红色
                expanded_img_data[y:y+stride_y, x:x+stride_x] = [255, 0, 0]  # 红色
            else:  # 白色
                expanded_img_data[y:y+stride_y, x:x+stride_x] = [255, 255, 255]  # 白色
    
    return Image.fromarray(expanded_img_data)


# 6. 恢复图像的主函数
def restore_image_from_bitstring(encoded_data, width, height, stride_x=4, stride_y=4):
    # 解码游程编码
    bit_string = run_length_decoding(encoded_data)
    
    # 将比特串恢复为图像数据
    img = bitstring_to_image(bit_string, width, height, stride_x, stride_y)
    
    return img


# 7. 使用示例
def main():
    image_path = '下载.png'  # 输入图片路径
    width, height = 204, 192  # 原图尺寸
    stride_x, stride_y = 4, 4  # 下采样参数

    # 将图片转换为比特串
    bit_string = image_to_bitstring(image_path, stride_x=stride_x, stride_y=stride_y)

    # 对比特串进行游程编码
    encoded_data = run_length_encoding(bit_string)

    # 输出游程编码到txt文件
    file_path = 'encoded_bitstring.txt'
    write_encoded_to_file(encoded_data, file_path)

    # 恢复压缩后的图像
    restored_img = restore_image_from_bitstring(encoded_data, width, height, stride_x, stride_y)

    # 保存恢复后的图像
    restored_img.save("restored_image.png")
    restored_img.show()


if __name__ == "__main__":
    main()
