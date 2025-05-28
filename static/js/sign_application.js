document.addEventListener("DOMContentLoaded", async () => {
  const signButton = document.getElementById("signButton");
  const statusBox = document.getElementById("status");
  const configElement = document.getElementById("sign-config");

  if (!signButton || !configElement) return;

  const config = JSON.parse(configElement.textContent);
  const { endpoint, csrf, uid } = config;

  signButton.addEventListener("click", async () => {
    signButton.disabled = true;
    statusBox.textContent = "Подключение к NCALayer...";

    const client = new NCALayerClient();

    try {
      await client.connect();
    } catch (err) {
      signButton.disabled = false;
      statusBox.textContent = "Не удалось подключиться к NCALayer.";
      alert(err.toString());
      return;
    }

    const originalData = btoa(uid);
    statusBox.textContent = "Выполняется подписание...";

    let signedData;
    try {
      signedData = await client.basicsSignCMS(
        NCALayerClient.basicsStorageAll,
        originalData,
        NCALayerClient.basicsCMSParamsAttached,
        NCALayerClient.basicsSignerSignAny
      );
    } catch (err) {
      signButton.disabled = false;
      statusBox.textContent = "Подпись не выполнена.";
      alert("Ошибка подписи: " + err.toString());
      return;
    }

    if (signedData.includes("-----BEGIN CMS-----")) {
      signedData = signedData
        .replace("-----BEGIN CMS-----", "")
        .replace("-----END CMS-----", "")
        .replace(/\r?\n|\r/g, "")
        .trim();
    }

    statusBox.textContent = "Отправка на сервер...";

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf,
        },
        body: JSON.stringify({
          signedData,
          originalData
        }),
      });

      const result = await response.json();

      if (result.success) {
        statusBox.textContent = "Заявка успешно подписана.";
        window.location.href = result.redirectUrl || "/";
      } else {
        signButton.disabled = false;
        statusBox.textContent = "Ошибка подписи: " + (result.message || "Неизвестная ошибка");
      }
    } catch (err) {
      signButton.disabled = false;
      statusBox.textContent = "Ошибка соединения с сервером.";
      alert(err.toString());
    }
  });
});
