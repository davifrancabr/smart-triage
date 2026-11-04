import json
import os

from openai import OpenAI


class ClassificadorIA:
    def __init__(self, api_key: str = None):
        """
        Inicializa o cliente de Inteligência Artificial.
        Pode receber a chave diretamente ou buscar nas variáveis de ambiente.
        """
        self.__api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.__client = OpenAI(api_key=self.__api_key) if self.__api_key else None

    def analisar_sintomas(self, descricao_sintomas: str) -> dict:
        """
        Recebe a descrição textual dos sintomas do paciente e utiliza IA
        para sugerir a classificação de risco (Vermelho, Amarelo, Verde).
        """
        prompt = (
            "Atue como um médico triagista especializado no Protocolo de Manchester. "
            "Analise os sintomas descritos pelo paciente e retorne EXCLUSIVAMENTE um objeto JSON "
            "com exatamente duas chaves:\n"
            "1. 'risco': contendo apenas um dos valores ('Vermelho', 'Amarelo', 'Verde').\n"
            "2. 'justificativa': uma breve explicação clínica da decisão.\n\n"
            f"Sintomas relatados: \"{descricao_sintomas}\""
        )

        try:

            if self.__client:
                response = self.__client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Você é um assistente médico de triagem de urgência."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                resultado_json = json.loads(response.choices[0].message.content)
                return {
                    "risco": resultado_json.get("risco", "Verde"),
                    "justificativa": resultado_json.get("justificativa", "Classificação padrão.")
                }

            else:

                desc_lower = descricao_sintomas.lower()
                if any(termo in desc_lower for termo in
                       ["peito", "respirar", "inconsciente", "sangue", "infarto", "derrame"]):
                    return {
                        "risco": "Vermelho",
                        "justificativa": "Sintomas indicam risco iminente à vida (emergência médica absoluta)."
                    }
                elif any(termo in desc_lower for termo in ["febre", "dor forte", "vômito", "tontura", "fratura"]):
                    return {
                        "risco": "Amarelo",
                        "justificativa": "Condição moderada que requer atendimento rápido, porém sem risco imediato de óbito."
                    }
                else:
                    return {
                        "risco": "Verde",
                        "justificativa": "Caso eletivo ou de baixo risco, apto para aguardar atendimento ambulatorial."
                    }

        except Exception as e:

            return {
                "risco": "Amarelo",
                "justificativa": f"Erro na integração com IA ({str(e)}). Direcionado para avaliação manual por precaução."
            }
