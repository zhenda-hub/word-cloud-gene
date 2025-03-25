from .celery_app import celery_app
from .config import settings  # 导入配置
import jieba
from wordcloud import WordCloud
import os
from pathlib import Path
import logging
import random

logger = logging.getLogger(__name__)


def load_stop_words():
    try:
        # 使用固定的停用词文件路径
        stop_words_path = os.path.join(os.path.dirname(__file__), 'stop_words.txt')
        log_msg = f"加载停用词文件: {stop_words_path}"
        logger.info(log_msg)
        with open(stop_words_path, 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f.readlines()])
    except Exception as e:
        logger.error(f"加载停用词失败: {str(e)}")
        return set()


# 全局停用词集合
STOP_WORDS = load_stop_words()


@celery_app.task(name="generate_wordcloud")
def generate_wordcloud(file_path: str, custom_stop_words: list[str] = None):
    # 合并默认停用词和用户自定义停用词
    stop_words = STOP_WORDS.copy()
    if custom_stop_words:
        stop_words.update(set(custom_stop_words))
    try:
        logger.info(f"开始处理文件: {file_path}")
        logger.info(f"当前停用词数量: {len(STOP_WORDS)}")
        
        # 确保文件存在
        if not os.path.exists(file_path):
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": "文件不存在"
            }

        # 读取文件内容
        logger.info("读取文件内容")
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'step': '读取文件'}
        )
        
        # 尝试以文本方式读取文件
        text = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # 如果 UTF-8 读取失败，尝试二进制读取
            with open(file_path, 'rb') as f:
                content = f.read()
                # 尝试不同的编码
                encodings = ['gbk', 'gb2312', 'gb18030', 'latin1']
                for encoding in encodings:
                    try:
                        text = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not text:
                    # 如果所有编码都失败，尝试二进制到文本的转换
                    text = ' '.join(f'{b:02x}' for b in content)
        
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 20, 'step': '读取文件完成'}
        )
        
        # 使用结巴分词并过滤停用词
        logger.info("进行分词")
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'step': '分词处理'}
        )
        word_list = list(jieba.cut(text))
        logger.info(f"分词前总词数: {len(word_list)}")
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 40, 'step': '分词完成'}
        )
        
        # 过滤停用词
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'step': '过滤停用词'}
        )
        filtered_words = [
            word for word in word_list 
            if word.strip() and word not in STOP_WORDS
        ]
        logger.info(f"过滤后词数: {len(filtered_words)}")
        words = ' '.join(filtered_words)
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 60, 'step': '过滤完成'}
        )
        
        # 生成词云图
        logger.info("生成词云图")
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 70, 'step': '生成词云'}
        )
        # 随机选择颜色方案和布局参数
        color_maps = ['rainbow', 'viridis', 'plasma', 'inferno', 'magma', 'cividis']
        real_color = random.choice(color_maps)
        logger.info(f"选择颜色方案: {real_color}")
        wc = WordCloud(
            font_path='/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
            width=800,
            height=400,
            colormap=real_color,
            background_color='white',
            stopwords=stop_words
        )
        wc.generate(words)
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 80, 'step': '生成词云完成'}
        )
        
        # 使用配置中的上传目录
        input_file = Path(file_path)
        input_stem = input_file.stem  # 这会包含时间戳
        output_filename = f"{input_stem}.png"  # 使用相同的时间戳
        output_path = os.path.join(settings.UPLOAD_FOLDER, output_filename)
        
        # 保存词云图
        logger.info(f"保存词云图到: {output_path}")
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'step': '保存图片'}
        )
        wc.to_file(output_path)
        generate_wordcloud.update_state(
            state='PROGRESS',
            meta={'progress': 95, 'step': '保存完成'}
        )
        
        # 返回相对路径和停用词信息
        relative_path = os.path.basename(output_path)
        logger.info(f"处理完成，返回路径: {relative_path}")
        
        # 如果有自定义停用词，将其格式化为字符串
        stop_words_text = ', '.join(custom_stop_words) if custom_stop_words else ''
        
        return {
            "status": "success",
            "image_path": relative_path,
            "stop_words": stop_words_text
        }
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }