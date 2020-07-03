export default `
    :host {
        display: inline-block;
        position: relative;
    }

    button {
        align-items: center;
        border-radius: 20px;
        border: none;
        cursor: pointer;
        display: flex;
        height: 40px;
        justify-content: center;
        outline: none;
        padding: 8px 20px;
        user-select: none;
    }

    .primary {
        background-color: var(--colour-red-80);
        color: var(--colour-white-100);

        &:hover {
            background-color: var(--colour-red-100);
        }

        &:active {
            background-color: var(--colour-red-50);
        }

        &:disabled {
            background-color: var(--colour-black-10);
        }
    }

    .secondary {
        background-color: var(--colour-blue-deep-80);
        color: var(--colour-white-100);

        &:hover {
            background-color: var(--colour-blue-deep-100);
        }

        &:active {
            background-color: var(--colour-blue-deep-50);
        }

        &:disabled {
            background-color: var(--colour-black-10);
        }
    }

    .tertiary {
        background-color: var(--colour-white-100);
        border: 2px solid var(--colour-blue-deep-80);
        color: var(--colour-blue-deep-80);

        &:hover {
            border-color: var(--colour-blue-deep-100);
            color: var(--colour-blue-deep-100);
        }

        &:active {
            border-color: var(--colour-blue-deep-50);
            color: var(--colour-blue-deep-50);
        }

        &:disabled {
            border-color: var(--colour-black-10);
            color: var(--colour-black-10);
        }
    }

    .large {
        border-radius: 25px;
        height: 50px;
        padding: 0 48px;
    }

    .content {
        font-family: 'FS Lucas', sans-serif;
        font-size: 16px;
        font-style: normal;
        font-weight: normal;
        letter-spacing: 1.08px;
        line-height: 26px;

        .loading & {
            visibility: hidden;
        }

        @nest .tertiary & {
            line-height: 24px;
        }
    }

    .large .content {
        font-size: 20px;
    }

    great-spinner {
        left: calc(50% - 10px);
        position: absolute;
        top: calc(50% - 12px);
    }

    great-icon {
        margin-right: 6px;

        .loading & {
            visibility: hidden;
        }
    }
`
