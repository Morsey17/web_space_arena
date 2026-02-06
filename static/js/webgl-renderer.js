class TextureManager {
    constructor() {
        this.textures = new Map();
    }

    async loadTexture(name, url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                this.textures.set(name, img);
                console.log(`✅ Загружена текстура: ${name} (${img.width}x${img.height})`);
                resolve(img);
            };
            img.onerror = (e) => {
                console.error(`❌ Ошибка загрузки текстуры ${name}:`, url, e);
                reject(new Error(`Не удалось загрузить текстуру: ${name}`));
            };
            img.src = url;
        });
    }

    async loadAll(basePath) {
        console.log(`📁 Загрузка текстур из: ${basePath}`);
        
        const textureList = [
            ['ship', 'ship.png'],
            ['drone', 'drone.png'],
            ['titan', 'titan.png'],
            ['tower', 'tower.png'],
            ['bullet', 'bullet.png'],
            ['missile', 'missile.png']
        ];

        try {
            await Promise.all(textureList.map(([name, file]) => 
                this.loadTexture(name, basePath + file)
            ));
            console.log('✅ Все текстуры загружены');
        } catch (error) {
            console.error('❌ Ошибка загрузки текстур:', error);
            throw error;
        }
    }

    getTexture(name) {
        const tex = this.textures.get(name);
        if (!tex) {
            console.warn(`⚠️ Текстура "${name}" не найдена`);
        }
        return tex;
    }
}

class WebGLRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.gl = this.initWebGL();
        if (!this.gl) {
            throw new Error('WebGL не поддерживается');
        }

        this.textureManager = new TextureManager();
        this.program = null;
        this.buffers = {};
        this.glTextures = new Map();
        this.teamColors = {
            red: [1.0, 0.0, 0.0],
            blue: [0.0, 0.0, 1.0]
        };

        this.cameraX = 0;
        this.cameraY = 0;
        this.cameraScale = 0.8; // Масштаб камеры (1 = нормальный)
        this.gameWidth = 4000;
        this.gameHeight = 4000;
        
        this.isReady = false;
    }

    async init(texturesBasePath) {
        try {
            console.log('🔄 Начинаем инициализацию WebGL...');
            
            // 1. Загружаем текстуры
            await this.textureManager.loadAll(texturesBasePath);
            
            // 2. Инициализируем шейдеры и буферы
            this.initShaders();
            this.initBuffers();
            
            // 3. Создаем WebGL текстуры
            this.createTextures();
            
            // 4. Устанавливаем флаг готовности
            this.isReady = true;
            console.log('✅ WebGL рендерер готов к работе!');
            
            return true;
        } catch (error) {
            console.error('❌ Ошибка инициализации WebGL:', error);
            this.isReady = false;
            throw error;
        }
    }

    initWebGL() {
        const gl = this.canvas.getContext('webgl', {
            alpha: true,
            antialias: false,
            powerPreference: 'high-performance'
        }) || this.canvas.getContext('experimental-webgl');

        if (!gl) {
            console.warn('WebGL не доступен');
            return null;
        }

        // Базовые настройки
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
        gl.clearColor(0.0, 0.0, 0.0, 0.0);
        
        return gl;
    }

    createTextures() {
        const gl = this.gl;
        this.glTextures.clear();
        
        for (const [name, image] of this.textureManager.textures) {
            try {
                const texture = gl.createTexture();
                gl.bindTexture(gl.TEXTURE_2D, texture);
                
                // Загружаем изображение
                gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
                
                // Настройки для пиксельной графики
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
                gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
                
                this.glTextures.set(name, texture);
                console.log(`✅ WebGL текстура создана: ${name}`);
            } catch (error) {
                console.error(`❌ Ошибка создания текстуры ${name}:`, error);
            }
        }
    }

    initShaders() {
        // Вершинный шейдер с поддержкой масштабирования
        const vsSource = `
            attribute vec2 a_position;
            attribute vec2 a_texCoord;
            
            uniform vec2 u_resolution;
            uniform vec2 u_translation;
            uniform float u_scale;
            uniform float u_rotation;
            uniform float u_camera_scale;
            
            varying vec2 v_texCoord;
            
            void main() {
                // Поворот
                float cosR = cos(u_rotation);
                float sinR = sin(u_rotation);
                vec2 rotated = vec2(
                    a_position.x * cosR - a_position.y * sinR,
                    a_position.x * sinR + a_position.y * cosR
                );
                
                // Масштаб объекта и камеры
                vec2 scaled = rotated * u_scale;
                
                // Позиция с учетом масштаба камеры
                vec2 position = scaled + u_translation;
                
                // Применяем масштаб камеры (делим координаты на scale)
                position = position / u_camera_scale;
                
                // Конвертация в координаты WebGL
                vec2 zeroToOne = position / u_resolution;
                vec2 zeroToTwo = zeroToOne * 2.0;
                vec2 clipSpace = zeroToTwo - 1.0;
                
                gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
                v_texCoord = a_texCoord;
            }
        `;

        // Фрагментный шейдер
        const fsSource = `
            precision mediump float;
            
            varying vec2 v_texCoord;
            uniform sampler2D u_texture;
            uniform vec3 u_color;
            uniform float u_alpha;
            
            void main() {
                vec4 texColor = texture2D(u_texture, v_texCoord);
                
                // Если пиксель прозрачный - отбрасываем
                if (texColor.a < 0.1) discard;
                
                // Раскрашиваем в цвет команды
                float brightness = (texColor.r + texColor.g + texColor.b) / 3.0;
                vec3 finalColor = u_color * brightness;
                
                gl_FragColor = vec4(finalColor, texColor.a * u_alpha);
            }
        `;

        this.program = this.createProgram(vsSource, fsSource);
        if (!this.program) {
            throw new Error('Не удалось создать шейдерную программу');
        }
    }

    createProgram(vsSource, fsSource) {
        const gl = this.gl;
        
        const vertexShader = this.compileShader(gl.VERTEX_SHADER, vsSource);
        const fragmentShader = this.compileShader(gl.FRAGMENT_SHADER, fsSource);
        
        if (!vertexShader || !fragmentShader) {
            return null;
        }
        
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Ошибка линковки шейдеров:', gl.getProgramInfoLog(program));
            return null;
        }
        
        return program;
    }

    compileShader(type, source) {
        const gl = this.gl;
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Ошибка компиляции шейдера:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        
        return shader;
    }

    initBuffers() {
        const gl = this.gl;
        
        // Вершины квадрата (центр в 0,0)
        const positions = new Float32Array([
            -0.5, -0.5,
             0.5, -0.5,
            -0.5,  0.5,
             0.5,  0.5
        ]);
        
        // Текстурные координаты
        const texCoords = new Float32Array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0
        ]);
        
        // Индексы для двух треугольников
        const indices = new Uint16Array([
            0, 1, 2,
            2, 1, 3
        ]);
        
        // Создаем буферы
        this.positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);
        
        this.texCoordBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.texCoordBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, texCoords, gl.STATIC_DRAW);
        
        this.indexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
        
        this.vertexCount = indices.length;
    }

    drawSprite(textureName, x, y, team, size = 30, rotation = 0, alpha = 1.0) {
        //alpha = 1.0;
        // Проверка готовности
        if (!this.isReady) {
            console.warn('⚠️ Рендерер не готов для отрисовки');
            return;
        }
        
        if (!this.glTextures.has(textureName)) {
            console.warn(`⚠️ Текстура "${textureName}" не найдена в WebGL`);
            return;
        }
        
        const gl = this.gl;
        
        // Нормализуем координаты с учетом масштаба камеры
        let normX = x - this.cameraX;
        let normY = y - this.cameraY;
        
        // Зацикливание карты
        if (normX > this.gameWidth / 2) normX -= this.gameWidth;
        else if (normX < -this.gameWidth / 2) normX += this.gameWidth;
        if (normY > this.gameHeight / 2) normY -= this.gameHeight;
        else if (normY < -this.gameHeight / 2) normY += this.gameHeight;
        
        // Преобразуем в экранные координаты с учетом масштаба камеры
        normX = normX / this.cameraScale + this.canvas.height / 2;
        normY = normY / this.cameraScale + this.canvas.height / 2;
        
        // Используем шейдерную программу
        gl.useProgram(this.program);
        
        // Находим location атрибутов
        const positionLocation = gl.getAttribLocation(this.program, 'a_position');
        const texCoordLocation = gl.getAttribLocation(this.program, 'a_texCoord');
        
        // Устанавливаем атрибуты
        gl.enableVertexAttribArray(positionLocation);
        gl.bindBuffer(gl.ARRAY_BUFFER, this.positionBuffer);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
        
        gl.enableVertexAttribArray(texCoordLocation);
        gl.bindBuffer(gl.ARRAY_BUFFER, this.texCoordBuffer);
        gl.vertexAttribPointer(texCoordLocation, 2, gl.FLOAT, false, 0, 0);
        
        // Находим location uniform переменных
        const resolutionLocation = gl.getUniformLocation(this.program, 'u_resolution');
        const translationLocation = gl.getUniformLocation(this.program, 'u_translation');
        const scaleLocation = gl.getUniformLocation(this.program, 'u_scale');
        const rotationLocation = gl.getUniformLocation(this.program, 'u_rotation');
        const cameraScaleLocation = gl.getUniformLocation(this.program, 'u_camera_scale');
        const textureLocation = gl.getUniformLocation(this.program, 'u_texture');
        const colorLocation = gl.getUniformLocation(this.program, 'u_color');
        const alphaLocation = gl.getUniformLocation(this.program, 'u_alpha');
        
        // Устанавливаем uniform переменные
        gl.uniform2f(resolutionLocation, this.canvas.width, this.canvas.height);
        gl.uniform2f(translationLocation, normX, normY);
        gl.uniform1f(scaleLocation, size);
        gl.uniform1f(rotationLocation, rotation);
        gl.uniform1f(cameraScaleLocation, this.cameraScale);
        
        // Цвет команды
        const teamColor = team === 0 ? this.teamColors.red : this.teamColors.blue;
        gl.uniform3f(colorLocation, teamColor[0], teamColor[1], teamColor[2]);
        gl.uniform1f(alphaLocation, alpha);
        
        // Активируем текстуру
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, this.glTextures.get(textureName));
        gl.uniform1i(textureLocation, 0);
        
        // Рисуем
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.drawElements(gl.TRIANGLES, this.vertexCount, gl.UNSIGNED_SHORT, 0);
    }

    clear() {
        if (!this.isReady) return;
        const gl = this.gl;
        gl.clear(gl.COLOR_BUFFER_BIT);
    }

    setCamera(x, y) {
        this.cameraX = x;
        this.cameraY = y;
    }

    setCameraScale(scale) {
        this.cameraScale = scale;
        console.log(`📐 Масштаб камеры изменен: ${scale}`);
    }

    renderGameState(gameState) {
        if (!this.isReady) {
            console.warn('⏳ WebGL рендерер еще не готов, пропускаем отрисовку');
            return;
        }
        
        this.clear();
        
        // Находим наш корабль для камеры
        if (window.sid) {
            for (let team_i = 0; team_i < 2; team_i++) {
                for (const ship of gameState.ship[team_i]) {
                    if (ship.sid === window.sid) {
                        this.setCamera(ship.x, ship.y);
                        break;
                    }
                }
            }
        }
        
        // Рисуем объекты
        try {
            for (let team_i = 0; team_i < 2; team_i++) {
                // Корабли
                for (const obj of gameState.ship[team_i]) {
                    const angle = Math.atan2(obj.direction_y, obj.direction_x);
                    this.drawSprite('ship', obj.x, obj.y, team_i, obj.radius * 2, angle, obj.health);
                }
                
                // Дроны
                for (const obj of gameState.drone[team_i]) {
                    const angle = Math.atan2(obj.direction_y, obj.direction_x);
                    this.drawSprite('drone', obj.x, obj.y, team_i, obj.radius * 2, angle, obj.health);
                }
                
                // Титаны
                for (const obj of gameState.titan[team_i]) {
                    this.drawSprite('titan', obj.x, obj.y, team_i, obj.radius * 2, 0, obj.health);
                }
                
                // Башни
                for (const obj of gameState.tower[team_i]) {
                    this.drawSprite('tower', obj.x, obj.y, team_i, obj.radius * 2, 0, obj.health);
                }
                
                // Пули
                for (const obj of gameState.bullet[team_i]) {
                    for (let i = 2; i >= 0; i--)
                        this.drawSprite('bullet', 
                            obj.x - obj.direction_x * i / 3 * obj.speed,
                            obj.y - obj.direction_y * i / 3 * obj.speed,
                            team_i,
                            obj.radius,
                            0,
                            (1 - i / 3));
                }
                
                // Ракеты
                for (const obj of gameState.missile[team_i]) {
                    const angle = Math.atan2(obj.direction_y, obj.direction_x);
                    this.drawSprite('missile', obj.x, obj.y, team_i, obj.radius * 4, angle);
                }
            }
        } catch (error) {
            console.error('❌ Ошибка при рендеринге:', error);
        }
    }
}