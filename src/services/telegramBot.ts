import logger from "@shared/Logger";
import axios from "axios";

interface ITelegramBot {
    chat_id: string;
    parse_mode: string;
    text?: string;
    sticker?: string;
 }

class Telegram {
    private baseUrl: string = 'https://api.telegram.org/bot';
    private token: string;
    private parseMode: string;
    private chatId: string;
    private params: ITelegramBot;

    constructor(
        token: string, 
        chatId: string, parseMode: string = 'MarkdownV2',
    )  {
        this.token = token;
        this.parseMode = parseMode;
        this.chatId = chatId;
        this.params = { 
            chat_id: this.chatId,
            parse_mode: this.parseMode
        }
    }

    public async sendMessage(message: string, type: string = 'text'): Promise<unknown> {
        const endPoint = type === 'text' ? 'sendMessage' : 'sendSticker';
        const url = new URL(`${this.baseUrl}${this.token}/${endPoint}`);
        // Imagen de prueba
        const image = 'https://s.tcdn.co/8a1/9aa/8a19aab4-98c0-37cb-a3d4-491cb94d7e12/19.png';
        const hasText = type === 'text';
        this.params[hasText ? 'text' : 'sticker'] = hasText ? message : image;

        const _getKeyValue_ = (key: string) => (obj: Record<string, any>) => obj[key];

        Object.keys(this.params).forEach(key => url.searchParams.append(key, _getKeyValue_(key)(this.params)));

        return axios.post(url.toString());
    } 

}

export default Telegram;